# Cluster reconfiguration

Cluster reconfiguration is the process of changing a cluster's resource configuration, topology, or membership while preserving the system's correctness and, ideally, its availability.

In stateful distributed systems, reconfiguration is particularly challenging because compute resources are not interchangeable: they may own partitions, maintain indexes, hold in-memory state, or process streams of updates.

The fundamental problem is:

**How can a distributed system replace its running infrastructure without interrupting ongoing computation or losing state?**

## 1. The problem: compute resources are stateful

Consider a distributed database running on three worker nodes.

```text
             Incoming Queries
                     |
                     v
             +---------------+
             | Query Router  |
             +---------------+
                     |
     +---------------+---------------+
     |               |               |
     v               v               v
+--------+      +--------+      +--------+
| Node A |      | Node B |      | Node C |
|        |      |        |      |        |
| State  |      | State  |      | State  |
|   P0   |      |   P1   |      |   P2   |
+--------+      +--------+      +--------+
```

Each node maintains state corresponding to a partition of the dataset.

Suppose the cluster needs to change its configuration:

- Increase CPU or memory capacity.
- Add or remove workers.
- Move workloads between machines.
- Change resource allocations.
- Replace unhealthy or outdated infrastructure.

In a stateless service, replacing a worker is relatively straightforward: start a new instance, verify its health, and route traffic to it.

In a stateful system, a new worker may need to reconstruct substantial internal state before it can process queries correctly.

```text
Old worker:
  Has state
  Has indexes
  Knows processing progress
  Can serve queries

New worker:
  Has no state
  Has no indexes
  Has not caught up
  Cannot safely serve queries yet
```

Simply terminating the old worker and starting a new one introduces downtime.

The cluster must solve two different problems:

1. **State reconstruction:** Prepare new resources to execute the workload.
2. **Safe handover:** Transfer responsibility to those resources without violating correctness or availability.

These problems are related but distinct.

## 2. Graceful reconfiguration: provision before retirement

**The fundamental pattern is create-before-destroy, often implemented as a form of blue-green replacement.**

Instead of immediately removing the existing resources, new resources are provisioned alongside them.

### Phase 1: The existing cluster is serving traffic

```text
  Query Router
        |
        v
+---------------+
|   Replica A   |
|               |
|     4 CPU     |
|   Hydrated    |
|    Serving    |
+---------------+
```

Suppose the desired configuration requires 8 CPUs.

### Phase 2: Provision a replacement

```text
  Query Router
        |
        v
+---------------+               +---------------+
|   Replica A   |               |   Replica B   |
|               |               |               |
|     4 CPU     |               |     8 CPU     |
|    Serving    |               |   Hydrating   |
+---------------+               +---------------+
```

The old replica remains operational while the replacement initializes.

### Phase 3: Wait until the new replica is ready

The replacement reconstructs its state, builds indexes, and processes updates until it reaches a suitable readiness point.

```text
                             Replacement preparation
                                        |
                                        v
+---------------+               +---------------+
|   Replica A   |               |   Replica B   |
|               |               |               |
|     4 CPU     |               |     8 CPU     |
|    Serving    |               |   Hydrated    |
|               |               |     Ready     |
+---------------+               +---------------+
```

A key distinction:

**Provisioned does not mean ready.**

An infrastructure provider might report that a new machine is healthy while the distributed database running on that machine is still rebuilding its state.

### Phase 4: Handover and retirement

Once the new replica is ready, the control plane can make it responsible for serving the workload and retire the old replica.

```text
  Query Router
        |
        v
+---------------+
|   Replica B   |
|               |
|     8 CPU     |
|    Serving    |
+---------------+

Replica A retired
```

The system has changed its resource configuration without requiring a period in which no hydrated replica is available.

This is the essence of graceful cluster reconfiguration.

## 3. Why the reconfiguration should run in the background

A naive implementation couples the reconfiguration process to the command that initiated it.

```text
         Client
            |
            | Request resize
            v
       Coordinator
            |
            | Create replacement
            | Wait for hydration
            | Retire old replica
            |
            v
Client receives response
```

This design has important limitations.

A stateful replacement might take minutes to complete. If the operation depends on the client connection or command execution context remaining alive, disconnects complicate recovery and progress.

The better architectural pattern is to separate declaring a desired state from achieving that state.

```text
         Client
            |
            | Request: desired size = 8 CPU
            v
+----------------------+
| Coordinator          |
|                      |
| Persist new intent   |
+----------------------+
            |
            | Acknowledge accepted change
            v
  Client can disconnect


 BACKGROUND CONTROL LOOP

+-----------------------+
| Reconfiguration       |
| Controller            |
|                       |
| Observe current state |
| Compare desired state |
| Reconcile differences |
+-----------------------+
            |
            v
+-----------------------+
| Existing Replica      |
| New Replica           |
| Hydration Progress    |
+-----------------------+
```

Now the client request is short-lived, but the reconfiguration can be long-running.

**The request returns after the intent is durably recorded, not necessarily after the infrastructure change is complete.**

This is a fundamental distributed systems design pattern:

**Persist the desired outcome and let an independent reconciliation process drive the system toward it.**

## 4. The reconciliation model

A controller does not need to remember every step of an imperative reconfiguration procedure.

Instead, it computes the difference between the desired and observed cluster state.

Suppose a cluster has two replicas, each with 4 CPUs, and needs to transition to two replicas with 8 CPUs each.

Initially:

```text
Realized configuration:
    2 x 4 CPU

Requested target:
    2 x 8 CPU

Observed replicas:
    A (4 CPU)
    B (4 CPU)
```

While reconfiguration is in progress, the controller combines two requirements:

```text
Baseline policy:
    Maintain 2 x 4 CPU

Reconfiguration policy:
    Prepare 2 x 8 CPU

Combined desired state:
    2 x 4 CPU
    2 x 8 CPU
```

The reconciliation loop computes:

```text
Desired replicas:
    A (4 CPU)
    B (4 CPU)
    C (8 CPU)
    D (8 CPU)

Observed replicas:
    A (4 CPU)
    B (4 CPU)

Difference:
    + Create C
    + Create D
```

After provisioning, the controller observes all four replicas.

While C and D hydrate, no further change is necessary.

When both become ready, the controller atomically updates the realized configuration to the new target:

```text
Before cutover:
    Baseline desires 2 x 4 CPU
    Reconfiguration desires 2 x 8 CPU

After cutover:
    Baseline desires 2 x 8 CPU
    Reconfiguration completed

Observed:
    A (4 CPU)
    B (4 CPU)
    C (8 CPU)
    D (8 CPU)

Difference:
    - Retire A
    - Retire B
```

Notice the architectural property: **the old replicas are retired because they are no longer desired, not because an imperative workflow reached a particular instruction.**

This makes the design naturally retryable and recoverable.

## 5. Concurrency: how to prevent stale reconfiguration decisions

Moving reconciliation into background tasks introduces an important correctness problem.

Consider the following race:

```text
Time    Controller             Coordinator
----    ----------             -----------

 T1     Reads desired size:
        8 CPU

 T2     Decides to remove
        old 4 CPU replicas

 T3                            Receives new request:
                               desired size = 4 CPU

 T4     Sends command:
        Remove 4 CPU replicas

 T5                            ???
```

The controller's decision was valid at T1 but became stale at T3.

Blindly applying it could remove resources that are now required.

The solution is optimistic concurrency control using a state witness.

```text
                   Controller
                        |
                        | Read state version V10
                        |
                        | Compute decision
                        |
                        | Send:
                        |   expected state = V10
                        |   changes = retire old replicas
                        v
                   Coordinator
                        |
                        | Is affected state still V10?
                        |
        +---------------+---------------+
        |                               |
       YES                             NO
        |                               |
        v                               v
Commit atomically                    Reject
                                        |
                                        v
                                 Reconcile again
```

The witness may include relevant cluster configuration and reconfiguration records rather than a single global version.

**The coordinator atomically validates the expected state and commits the mutation only if the decision is still valid.**

This separates two responsibilities:

- Controller: Computes what should happen, potentially in parallel.
- Coordinator: Decides whether the proposed state transition is still valid and commits it atomically.

It also enables multiple independent controllers to propose decisions without requiring them to coordinate every calculation with one another.

## 6. Failure handling

Graceful reconfiguration must account for more than successful hydration.

| Failure                          | Correct behavior                                    |
| -------------------------------- | --------------------------------------------------- |
| New replica fails to start       | Keep existing replicas                              |
| New replica never hydrates       | Timeout and normally roll back                      |
| Client disconnects               | Continue using persisted intent                     |
| Controller crashes               | Restart and reconstruct from durable state          |
| Configuration changes mid-flight | Reject stale decisions and recompute                |
| Insufficient resources           | Preserve baseline and fail the attempted transition |

A particularly important tradeoff concerns reconfiguration timeouts.

**Rollback on timeout:** Preserve the old configuration and abandon the replacement attempt. This favors availability.

**Force commit on timeout:** Replace the old configuration even though the new replicas are not fully hydrated. This favors completing the configuration change, but may introduce temporary unavailability or degraded performance.

**The default for a graceful transition should generally be rollback.**

There is also a distinction between hydrated and fully caught up. Depending on the system's consistency model, a hydrated replica can already answer correctly even when it has not processed every recent update. Requiring stronger catch-up before retirement may improve post-cutover latency, but also prolongs reconfiguration.

## 7. The tradeoffs

| Approach                         | Advantages                         | Disadvantages                                                      |
| -------------------------------- | ---------------------------------- | ------------------------------------------------------------------ |
| Stop and replace                 | Simple, low temporary cost         | Downtime                                                           |
| Create before destroy            | Preserves availability             | Temporary resource duplication                                     |
| Live state migration             | Potentially reduces reconstruction | Complex coordination and ownership transfer                        |
| Reconciliation-based replacement | Recoverable, modular, asynchronous | Requires durable intent, readiness signals and concurrency control |

One subtle point: **graceful reconfiguration does not necessarily require transferring state directly between the old and new replicas.**

If state can be reconstructed from durable storage or replayable inputs, independently hydrating new replicas may be architecturally simpler than live migration.

However, this shifts the cost to storage reads, network traffic, and temporary duplicate computation.

## 8. Engineering principles

Several general-purpose distributed systems patterns emerge.

1. **Separate desired state from realized state.** A requested configuration change is not the same as a completed configuration change.
2. **Use overlap for availability.** New resources should become ready before old resources lose responsibility.
3. **Keep long-running work outside critical coordination loops.** Centralized serialization should be reserved for operations that require authoritative ordering or atomic mutation.
4. **Persist intent, not execution context.** A process crash or client disconnect should not erase the requested outcome.
5. **Make reconciliation idempotent.** Repeating a reconciliation pass should not create duplicate resources or accidentally remove required ones.
6. **Validate decisions at commit time.** A correct decision based on stale state is no longer necessarily correct.
7. **Treat readiness as a correctness requirement.** A running process is not automatically capable of serving the workload.
8. **Define failure policies explicitly.** Rollback, retry, cancellation, and forceful cutover have different safety and availability implications.

## 9. The deeper architectural principle

Cluster reconfiguration can be understood as a controlled transition between two valid system configurations.

```text
  Configuration A
  (Old, serving)
         |
         v
+----------------+
| Persist target |
| configuration  |
+----------------+
         |
         v
+----------------+
| Provision B    |
| while A serves |
+----------------+
         |
         v
+----------------+
| Validate B     |
| readiness      |
+----------------+
         |
         v
+----------------+
| Atomic commit  |
| of cutover     |
+----------------+
         |
         v
+----------------+
| Retire A       |
+----------------+
         |
         v
  Configuration B
  (New, serving)
```

**The most important distinction is between the atomicity of the control-plane decision and the physical duration of the reconfiguration.**

The actual transition may take minutes, involve many asynchronous operations, and temporarily double the resource footprint. Yet the authoritative configuration change can still be a short, atomic transaction.

That separation makes it possible to build systems that are simultaneously adaptable, highly available, crash-recoverable, and internally modular.
