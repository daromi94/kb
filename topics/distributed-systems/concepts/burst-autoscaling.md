# Burst autoscaling

Burst autoscaling is a resource management strategy that temporarily provisions additional compute capacity to accelerate an expensive operation, then removes that capacity once it is no longer necessary.

The fundamental idea is to separate two resource requirements:

- **Transient capacity:** Resources required to initialize, recover, or prepare a system.
- **Steady-state capacity:** Resources required to operate the system after initialization.

These requirements can be dramatically different.

## 1. The problem: initialization is more expensive than execution

Consider a distributed database that maintains an in-memory index over a large dataset.

During normal operation, the system incrementally maintains the index as new records arrive.

However, when the index is first created, the system must process the entire existing dataset.

This initialization process is called hydration.

```text
INITIALIZATION (Hydration)

    Persistent Data
           |
           v
+--------------------+
| Read existing data |
+--------------------+
           |
           v
+--------------------+
| Process records    |
+--------------------+
           |
           v
+--------------------+
| Build in-memory    |
| indexes / state    |
+--------------------+
           |
           v
         READY


STEADY STATE

       New data
           |
           v
+--------------------+
| Incrementally      |
| update indexes     |
+--------------------+
           |
           v
         READY
```

These workloads have different resource profiles.

| Dimension           | Initialization            | Steady state                |
| ------------------- | ------------------------- | --------------------------- |
| Data processed      | Entire existing dataset   | New updates                 |
| CPU demand          | Potentially high          | Usually lower               |
| Memory demand       | State plus build overhead | Maintained state            |
| Duration            | Temporary                 | Continuous                  |
| Latency sensitivity | Time until ready          | Query latency and freshness |

A system sized for ordinary incremental processing might take several minutes to construct its initial state.

Provisioning larger compute resources permanently would reduce initialization latency but waste capacity during normal operation.

This creates a tradeoff:

Optimize for initialization performance or steady-state resource efficiency?

Burst autoscaling attempts to achieve both.

## 2. The solution: temporary additional replicas

Rather than permanently resizing the cluster, provision an additional, more powerful replica during hydration.

Consider:

- Replica A: Small, inexpensive, intended for steady-state operation.
- Replica B: Large, expensive, intended for rapid hydration.

Both replicas independently initialize their state.

```text
               Existing Dataset
                       |
        +--------------+--------------+
        |                             |
        v                             v
+---------------+             +---------------+
| Replica A     |             | Replica B     |
|               |             |               |
| Small         |             | Large         |
| Steady-state  |             | Temporary     |
+---------------+             +---------------+
        |                             |
        v                             v
 Slow hydration                Fast hydration
        |                             |
        |                             v
        |                        READY FIRST
        |                             |
        |                             v
        |                       Serve queries
        |                             |
        v                             |
READY + CAUGHT UP                     |
        |                             |
        +--------------+--------------+
                       |
                       v
               Retire Replica B
                       |
                       v
               +---------------+
               | Replica A     |
               |               |
               | Steady-state  |
               +---------------+
```

**The critical architectural detail is that the larger replica does not need to accelerate the smaller replica's hydration.**

Instead, it becomes ready earlier and provides usable capacity while the smaller replica continues hydrating independently.

This is a form of temporary overprovisioning combined with overlapping execution.

## 3. The lifecycle of a burst

Illustrative timeline — not measured performance data

```text
Time / condition        Replica B (burst)     Replica A (steady)
Start                   Hydrating             Hydrating
After 3 minutes         Ready / serving       Hydrating
After 9 minutes         Ready / serving       Ready / serving
Catch-up + linger       Retired               Ready / serving
```

Example: burst becomes ready after 3 minutes, steady replica after 9 minutes; the burst is retired after a readiness and linger period.

The lifecycle has four important phases:

1. Provision: The controller detects unhydrated state and requests an additional replica.
2. Hydrate: Both replicas construct their internal state independently.
3. Wait for catch-up: The smaller replica must become ready and sufficiently caught up to safely serve the workload.
4. Retire: After a configurable linger period, the temporary replica is removed.

The linger period prevents immediate retirement when readiness may be unstable. If readiness regresses, the countdown can restart.

## 4. Why readiness is more important than time

A naive design might provision temporary capacity for a fixed period:

```text
 Create burst
       |
       v
Wait 5 minutes
       |
       v
 Delete burst
```

This is dangerous.

What happens if the smaller replica requires ten minutes to hydrate?

Or never becomes ready?

Removing the burst would potentially make the system unavailable.

A better design makes retirement dependent on observed state:

```text
                          Burst running
                                |
                                v
                        Is steady ready?
                                |
      +-------------------------+
      |                         |
     NO                        YES
      |                         |
      v                         v
 Keep burst             Is it caught up?
                                |
      +-------------------------+
      |                         |
     NO                        YES
      |                         |
      v                         v
 Keep burst               Start linger
                                |
                                v
                        Recheck readiness
                                |
      +-------------------------+
      |                         |
    FAIL                      PASS
      |                         |
      v                         v
Reset linger                 Retire
```

This introduces an important principle:

**Resource retirement must depend on the ability of the remaining system to sustain the workload, not simply on elapsed time.**

A replica may have finished building its initial state but still be unable to process incoming updates fast enough.

**Readiness and sustained capacity are related but distinct.**

**If the smaller replica never catches up, retaining the burst preserves availability, but can result in an indefinitely elevated infrastructure cost.**

## 5. Burst autoscaling versus traditional autoscaling

Traditional autoscaling is primarily reactive to operational demand.

Burst autoscaling can instead respond to a known expensive lifecycle operation.

|            | Traditional autoscaling         | Hydration burst autoscaling                      |
| ---------- | ------------------------------- | ------------------------------------------------ |
| Trigger    | CPU, load, queues, traffic      | Unhydrated state                                 |
| Objective  | Handle increased ongoing demand | Reduce time until ready                          |
| Capacity   | Scale operational replicas      | Add temporary powerful replica                   |
| Scale-down | Lower demand                    | Steady replica is ready                          |
| Main risk  | Load oscillation                | Premature retirement or excessive burst lifetime |

In a traditional autoscaler:

```text
  Traffic increases
          |
          v
CPU utilization rises
          |
          v
      Scale out
          |
          v
 Capacity increases
```

In hydration-based burst autoscaling:

```text
   New state must be built
              |
              v
Provision temporary capacity
              |
              v
     Build state faster
              |
              v
  Steady replica catches up
              |
              v
  Remove temporary capacity
```

The second model is better described as lifecycle-aware autoscaling.

It uses domain-specific knowledge about the workload, rather than relying exclusively on generic infrastructure metrics.

## 6. Architectural tradeoffs

Three tradeoffs are particularly important.

Cost versus availability. A burst replica is expensive, but deleting it prematurely can interrupt service. Safety-oriented designs retain extra capacity until retirement is demonstrably safe.

Concurrent hydration versus resource contention. Running two replicas at once increases aggregate CPU, memory, and I/O demand. If both replicas compete for a saturated shared storage system, the larger replica may offer little improvement. **Burst capacity is useful only when the additional resources relieve the actual bottleneck.**

Automatic recovery versus complexity. A controller needs to survive crashes, retry failed provisioning attempts, and reconcile replica state. Persisting burst intent and deriving actions from current state avoids depending on one fragile, long-running imperative workflow.

## 7. Engineering lessons

The most reusable design lessons are:

- **Separate transient resource demands from steady-state resource requirements.** Initialization, restoration, catch-up, and migration may need a very different resource shape from ordinary operation.
- **Overlap work rather than blocking on replacement.** Maintain existing capacity while preparing new capacity.
- **Prefer semantic readiness signals.** An application-specific signal such as state hydration is often more meaningful than generic CPU utilization.
- **Make retirement conditional.** Remove temporary capacity only when remaining replicas can safely assume responsibility.
- **Make bursts best-effort.** Failure to provision an optimization should not prevent the baseline system from operating.
- **Design for an indefinitely extended burst.** A readiness failure can turn a temporary expense into a persistent one; budgets, alerts, and operator controls matter.

## The deeper principle

**Burst autoscaling is fundamentally about decoupling the resource configuration required to reach a desired state from the resource configuration required to maintain that state.**

```text
  System lifecycle

EXPENSIVE TRANSITION
          |
          v
+------------------+
| Extra resources  |
|                  |
| Reach readiness  |
+------------------+
          |
          v
    STEADY STATE
          |
          v
+------------------+
| Minimal adequate |
| resources        |
|                  |
| Maintain state   |
+------------------+
```

This principle applies beyond database hydration: rebuilding search indexes, restoring stateful stream processors, warming caches, recovering shards, loading models, or preparing replacement replicas.

**The essential insight is that the cheapest configuration for operating a system is not necessarily the best configuration for getting it ready to operate.**
