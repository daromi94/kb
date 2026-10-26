# Compute and Data: Locality vs. Independence

One of the fundamental architectural trade-offs in distributed systems is whether computation should be placed close to its data or whether computation and data should be managed independently.

These two design goals optimize different properties:

- Locality: Minimize the cost of accessing data by placing computation near the data it needs.
- Independence: Allow computation and data to scale, move, and evolve without requiring each other to move.

The challenge is that improving one often makes the other more difficult.

## 1. Compute and data are different resources

Consider a distributed system that processes financial transactions.

There are two distinct components.

Compute executes operations:

```
Read balance
Apply transaction
Validate constraints
Update balance
Generate result
```

Data represents the information those operations depend on:

```
account-1 -> balance: 1000
account-2 -> balance: 2500
account-3 -> balance: 4000
```

Conceptually:

```
             +------------------+
             | Compute          |
             |                  |
             | Execute logic    |
             | Transform data   |
             | Produce results  |
             +------------------+
                      |
                      | Read / Write
                      v
             +------------------+
             | Data             |
             |                  |
             | Application state|
             | Stored records   |
             | Indexes          |
             +------------------+
```

The compute component needs data to execute its operations, but there is no fundamental requirement that both reside on the same machine.

That placement decision creates the trade-off.

## 2. Locality: move compute close to data

Data locality is the principle of minimizing the distance between computation and the data it accesses.

Consider a cluster with two workers.

```
+-----------------------+
| Worker A              |
|                       |
|  +-----------------+  |
|  | Task A          |  |
|  |                 |  |
|  | Compute         |  |
|  |      |          |  |
|  |      v          |  |
|  | Local State     |  |
|  +-----------------+  |
|                       |
+-----------------------+


+-----------------------+
| Worker B              |
|                       |
|  +-----------------+  |
|  | Task B          |  |
|  |                 |  |
|  | Compute         |  |
|  |      |          |  |
|  |      v          |  |
|  | Local State     |  |
|  +-----------------+  |
|                       |
+-----------------------+
```

Each task accesses state stored on its own worker.

This is useful because local access avoids additional network operations.

### Why does locality improve performance?

There is a hierarchy of access costs:

```
               CPU Registers
                     |
                  L1 Cache
                     |
                  L2 Cache
                     |
                  L3 Cache
                     |
                  Local DRAM
                     |
                  Local SSD
                     |
               Network Access
                     |
              Remote Storage
```

This is a conceptual hierarchy, not a strict latency ranking for every device and workload. A local SSD operation, for example, can be slower than a remote memory access.

However, a network request generally introduces additional costs:

- Network transport and queuing.
- Serialization and deserialization.
- Remote request processing.
- Additional failure and timeout possibilities.

Suppose a stateful task processes 100,000 records per second.

If processing every record requires remote state access, network overhead can become significant.

With local state:

```
Record
   |
   v
Task
   |
   v
Local State
   |
   v
Process
```

With remote state:

```
Record
   |
   v
Task
   |
   | Network request
   v
Remote State
   |
   | Network response
   v
Task
   |
   v
Process
```

Locality reduces communication costs, often improving throughput and latency.

This motivates an important systems principle:

Move computation to data when moving data to computation would be more expensive.

It is particularly useful for data-intensive workloads where operations repeatedly access the same state.

## 3. Independence: move compute without moving data

Locality provides efficient access, but tightly coupling computation and data has consequences.

Suppose Task A owns 100 GB of state.

```
Worker A
+------------------------+
|                        |
| Task A                 |
|                        |
| Compute                |
|                        |
| State: 100 GB          |
|                        |
+------------------------+
```

Now suppose Worker A becomes overloaded.

The scheduler wants to relocate Task A to Worker B.

If computation and data must remain colocated:

```
Worker A                       Worker B
+-------------------+          +-------------------+
|                   |          |                   |
| Task A            |          |                   |
| State: 100 GB     |          |                   |
|                   |          |                   |
+-------------------+          +-------------------+
         |                               ^
         |                               |
         +------ Move 100 GB ------------+
```

A computational placement decision has become a storage migration problem.

The system cannot relocate the task cheaply because its state is tied to the old worker.

### What does independence change?

With independent computation and storage:

```
BEFORE

+-------------+
| Compute A   |
| Worker A    |
+-------------+
       |
       v
+-------------+
| State Store |
+-------------+


AFTER

+-------------+
| Compute A   |
| Worker B    |
+-------------+
       |
       v
+-------------+
| State Store |
+-------------+
```

The computational task moves, but the state remains where it was.

This is compute-data independence.

It enables separate lifecycle management for computation and storage.

For example, the system can scale the number of compute tasks without necessarily scaling or redistributing the storage layer.

However, if every operation now requires accessing remote state, steady-state performance may suffer.

## 4. Why locality and independence are in tension

Consider two architectures.

### Architecture A: tightly coupled compute and state

```
+--------------------+
| Worker 1           |
|                    |
| Compute A          |
|    |               |
|    v               |
| State A            |
+--------------------+

+--------------------+
| Worker 2           |
|                    |
| Compute B          |
|    |               |
|    v               |
| State B            |
+--------------------+
```

This architecture optimizes locality.

But if the system wants to change task ownership or placement, it may need to relocate state.

### Architecture B: disaggregated compute and state

```
       COMPUTE LAYER

+-------------+  +-------------+
| Compute A   |  | Compute B   |
+-------------+  +-------------+
       |                |
       +--------+-------+
                |
                | Network
                v

       STORAGE LAYER

+-------------------------+
| Distributed State Store |
+-------------------------+
```

This architecture optimizes independence.

Compute resources can be reassigned without necessarily moving the stored state.

But network access becomes part of the state-access path, unless caching or other optimizations eliminate it.

The resulting trade-off is:

| Property                              | Locality-oriented | Independence-oriented |
| ------------------------------------- | ----------------- | --------------------- |
| State access                          | Mostly local      | Potentially remote    |
| Normal processing latency             | Lower             | Potentially higher    |
| Compute relocation                    | More expensive    | Easier                |
| Independent scaling                   | More constrained  | More flexible         |
| State movement during reconfiguration | Often required    | Often avoidable       |
| Runtime network overhead              | Lower             | Potentially higher    |

Neither architecture is universally better.

The correct choice depends on the frequency and cost of state accesses relative to the frequency and cost of reconfiguration.

## 5. Can locality and independence coexist?

Yes, by separating logical ownership from physical state location and allowing state to move only when necessary.

Consider a system with two tasks.

Initially:

```
Task A                          Task B
+-------------------+           +-------------------+
| Owns: 1, 2        |           | Owns: 3, 4        |
|                   |           |                   |
| Stores: 1, 2      |           | Stores: 3, 4      |
+-------------------+           +-------------------+
```

Now suppose key 2 is reassigned to Task B.

Instead of immediately moving its state, the system transfers logical ownership.

```
Task A                          Task B
+-------------------+           +-------------------+
| Owns: 1           |           | Owns: 2, 3, 4     |
|                   |           |                   |
| Stores: 1, 2      |           | Stores: 3, 4      |
+-------------------+           +-------------------+
```

Task B is authorized to process key 2, but the associated state remains physically on Task A.

When Task B first needs key 2:

```
Task B                         Task A
   |                              |
   |---- Fetch state: key 2 ----->|
   |                              |
   |<--- State for key 2 ---------|
   |                              |
   v                              |
Store state locally               |
   |                              |
   v                              |
Process record                    |
```

Subsequent operations access local state.

```
Task A                          Task B
+-------------------+           +-------------------+
| Owns: 1           |           | Owns: 2, 3, 4     |
|                   |           |                   |
| Stores: 1         |           | Stores: 2, 3, 4   |
+-------------------+           +-------------------+
```

This produces an interesting combination:

- Independence during reconfiguration: Ownership can change before state moves.
- Locality during normal execution: Frequently accessed state eventually resides with the task processing it.

A correct implementation must still coordinate ownership handoffs, state transfers, and records already in flight so that no two tasks independently update the same key.

## 6. The importance of the working set

The effectiveness of this approach depends on another fundamental concept: the working set.

The working set is the subset of data actively accessed during a particular period.

Suppose a system maintains 1 TB of state.

```
Total State: 1 TB

+----------------------------------+
|                                  |
|  Hot State: 20 GB                |
|                                  |
|  Cold State: 980 GB              |
|                                  |
+----------------------------------+
```

Only 20 GB is frequently accessed.

Now suppose reconfiguration assigns half of all keys to new tasks.

An eager migration strategy might move approximately 500 GB of state.

A lazy migration strategy can avoid moving inactive state, migrating only reassigned keys actually accessed afterward.

If only 10 GB of the reassigned state becomes active:

```
Eager migration

500 GB transferred


Lazy migration

10 GB transferred
490 GB left in place
```

These figures are illustrative.

The key observation is that total state size and active state size are not necessarily correlated.

A system may accumulate enormous amounts of historical state while accessing only a small fraction at any given moment.

This is why temporal locality is so important for adaptive stateful systems.

If nearly every key is eventually accessed, however, lazy migration may still transfer most of the reassigned state.

## 7. A useful performance model

The architecture can be viewed as balancing two categories of cost.

Normal execution cost is paid while processing records:

\\[ C\_{\text{execution}} = C\_{\text{compute}} + C\_{\text{state access}} \\]

Reconfiguration cost is paid when the deployment changes:

\\[ C\_{\text{reconfiguration}} = C\_{\text{coordination}} + C\_{\text{migration}} + C\_{\text{disruption}} \\]

A locality-oriented system typically minimizes state-access cost but may incur higher migration and disruption costs.

An independence-oriented system typically reduces migration requirements but may pay more for remote accesses.

A hybrid architecture tries to keep both costs low by paying remote-access and migration costs only for state that actually needs to move.

The overall trade-off depends on workload characteristics, migration frequency, network capacity, state size, and access locality. The costs also interact: migration can compete with ordinary processing for CPU, memory, disk, and network resources.

## 8. A deeper principle: placement should follow access patterns

Consider three kinds of state.

Hot state: Frequently accessed by the same task. Keeping this state close to compute is usually beneficial.

Cold state: Rarely accessed. Moving it during every reconfiguration may waste resources.

Shared state: Accessed by multiple computational components. Keeping it in one local task may be unsuitable; replication, caching, or a shared storage service may be preferable, depending on consistency requirements.

This suggests a more general approach:

```
                 Data
                   |
                   v
           Access Characteristics
                   |
          +--------+--------+
          |        |        |
          v        v        v
         Hot      Cold     Shared
          |        |        |
          v        v        v
        Local    Leave     Shared or
        State    in place  Replicated
                            Storage
```

This is a conceptual policy rather than a universal rule.

An important distinction is that data locality should be driven by actual access patterns, not merely by logical ownership or total data size.

## 9. Architectural lessons

There are several broader lessons for distributed systems design.

First, computation and data have different resource requirements. CPU capacity may need to scale rapidly while stored state grows more slowly, or vice versa. Treating both as inseparable can lead to inefficient resource allocation.

Second, placement flexibility has a cost. Remote storage removes some migration dependencies but introduces network overhead, additional failure modes, and potential contention at shared storage services.

Third, locality does not necessarily require permanent colocation. A system can dynamically move active state toward computation while leaving inactive state elsewhere.

Finally, the decision to move computation should not automatically imply a decision to move all associated data.

The central architectural principle is to make computation and storage independently manageable while preserving locality for performance-critical accesses.

The difficult engineering problem is achieving both properties without compromising correctness, introducing excessive coordination, or making remote state access the dominant execution cost.
