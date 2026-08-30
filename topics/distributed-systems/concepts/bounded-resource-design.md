# Bounded resource design

Bounded resource design keeps a system predictable by deciding in advance
how much work and state it may accumulate. Just as importantly, it defines
what happens when the system reaches that limit.

The core tradeoff is:

> **A bounded system gives up the illusion that every request can be
> accepted so it can keep completing useful work under overload.**

## Why explicit bounds matter

When incoming work exceeds processing capacity, the difference has to go
somewhere.

Without an explicit limit, it usually accumulates:

```text
requests arrive faster than they complete
                    |
                    v
              queue grows
                    |
                    v
             memory grows
                    |
                    v
             latency grows
                    |
                    v
          timeouts and retries
```

The system appears to accept the load, but it is only postponing rejection.
By the time it fails, it has consumed memory, increased latency, and created
more work through retries.

With an explicit limit, overload becomes a controlled path:

```text
incoming work
      |
      v
+-------------------+
| bounded capacity  |
+-------------------+
      |
      +--> capacity available --> accept
      |
      +--> capacity exhausted --> wait, reject, shed, or spill
```

The bound does not increase capacity. It prevents the system from destroying
the capacity it still has.

## What should be bounded

Every form of accumulation needs its own limit. Bounding memory does not
bound execution time, and bounding concurrency does not bound persistent
state.

| Dimension         | Example limit                  | Behavior at the boundary              |
|-------------------|--------------------------------|---------------------------------------|
| Work per request  | Page, batch, or fan-out size   | Continue in another operation         |
| Concurrency       | In-flight operation count      | Wait, throttle, or reject             |
| Transient memory  | Queue, cache, or pool capacity | Apply backpressure or shed load       |
| Execution time    | Deadline or iteration count    | Cancel, yield, or return partial work |
| Recoverable state | Log, checkpoint, or shard size | Flush, compact, or repartition        |

These limits answer different questions:

```text
How much work can one request create?

How many operations can run at once?

How much state can wait in memory?

How long can an operation retain resources?

How much state must a failed component rebuild?
```

A system needs an answer for each question before overload supplies one.

## A limit is more than a number

A numeric ceiling is incomplete without a policy for crossing it. A queue
with space for 10,000 items still needs to decide what happens to item
10,001.

The system can:

- Block the producer until capacity returns.
- Reject the new item immediately.
- Remove older or lower-priority work.
- Spill transient state to a slower storage tier.
- Divide the work into another bounded operation.

The right response depends on the work. Durable writes may need to wait or
spill. Expired requests should be discarded. Interactive traffic may need a
fast rejection so the caller can choose another path.

The limit itself should come from a resource or latency budget. A queue that
is technically finite but takes 20 minutes to drain is effectively unbounded
for a request with a 2-second deadline.

## Bounded work is not bounded time

An algorithm can perform a known amount of work without having deterministic
latency.

For example:

```text
maximum iterations = 1,000
```

This bounds the number of iterations. It does not bound the duration of an
iteration that waits on storage, scheduling, or the network.

The relationship is:

```text
elapsed time
    depends on
bounded work + processing rate + external delays
```

A strict time bound therefore needs more than a finite loop. It also needs
reserved processing capacity, controlled dependencies, or a deadline that
stops the operation.

General-purpose distributed systems rarely control every source of delay.
Their limits create an envelope that can be measured and tested, not
perfectly deterministic latency.

## Static allocation is one memory strategy

Static allocation enforces a memory limit by reserving the required objects
before the system begins processing work.

```text
startup
  |
  v
reserve fixed pools
  |
  v
reuse objects during operation
  |
  v
never exceed reserved memory
```

This removes allocation and reclamation for those objects from the hot path.
It also avoids fragmentation within those pools. The cost is that memory is
reserved early, and the system has less flexibility when the workload
changes.

Static allocation is not the only bounded design:

| Strategy             | Memory behavior                                      |
|----------------------|------------------------------------------------------|
| Static allocation    | Reserve the maximum number of objects before serving |
| Bounded pool         | Allocate and recycle objects within a fixed capacity |
| Bounded arena        | Serve allocations from a fixed-size memory region    |
| Unbounded allocation | Keep allocating until another limit intervenes       |

A garbage-collected system can still enforce a memory bound by limiting
admitted work and the memory attributable to it.

The important invariant is:

> **Admitted work cannot make live memory grow beyond a known ceiling.**

## Recovery also needs explicit bounds

Recovery is another workload. A failed storage node may need to:

```text
detect the failure
start a replacement
transfer durable state
replay the write-ahead log
reconstruct in-memory indexes
inspect metadata and data files
```

The amount of recovery work matters because:

```text
recovery time ~= recovery work / recovery throughput
```

Storage engines control that numerator with several limits:

| Recovery work        | Mechanism that bounds it              |
|----------------------|---------------------------------------|
| Log replay           | Flushes, checkpoints, and log cleanup |
| Per-node state       | Sharding and tiering                  |
| Metadata history     | Snapshots and metadata compaction     |
| Index reconstruction | Persisted index state and checkpoints |

These mechanisms cap how much work recovery must perform. They do not create
a wall-clock guarantee by themselves.

Recovery throughput still depends on:

```text
storage bandwidth
network bandwidth
scheduling
available CPU
surviving replicas
competing foreground traffic
```

Predictable recovery therefore needs both sides of the equation:

```text
bounded recovery work
          +
reserved recovery capacity
          =
manageable recovery time
```

Mean time to recovery remains an average, not a deadline. The operational
goal is recovery headroom: the cluster restores capacity faster than
failures remove it.

## Bounds must compose end to end

A bounded component can still participate in an unbounded system.

Suppose the service has a bounded worker pool, but its proxy accepts an
unbounded queue:

```text
clients
   |
   v
+-------------------+
| unbounded proxy   |
| queue grows here  |
+-------------------+
   |
   v
+-------------------+
| bounded service   |
+-------------------+
```

The service protects its own memory, but the overload has only moved to the
proxy. The same failure occurs when bounded queues feed unlimited retries or
when bounded requests create unbounded fan-out downstream.

A complete design carries the limit to the point that can reduce demand:

```text
service reaches capacity
          |
          v
propagate pressure upstream
          |
          v
producer slows or admission rejects
```

Every layer must honor the limits of the layer below it.

## The tradeoff

Explicit limits exchange flexibility at the boundary for predictability
inside it.

| Benefit                  | Cost                                                |
|--------------------------|-----------------------------------------------------|
| Bounded memory use       | Some work must wait, spill, or be rejected          |
| Controlled overload      | Capacity limits must be selected and maintained     |
| Predictable work volume  | Large operations must be divided                    |
| Manageable recovery      | State needs checkpoints, partitions, or tiering     |
| Smaller failure cascades | Pressure must propagate across component boundaries |

Without explicit limits:

```text
accept work
    |
    v
accumulate hidden obligations
    |
    v
fail late and unpredictably
```

With explicit limits:

```text
measure capacity
    |
    v
accept bounded obligations
    |
    v
handle saturation deliberately
```

The strongest design principle is:

> **Every limit must answer two questions: what is the maximum obligation,
> and what does the system do when it reaches that maximum?**

---

Return to [Concepts](_index.md)
