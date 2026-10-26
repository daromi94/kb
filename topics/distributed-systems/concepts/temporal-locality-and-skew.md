# Temporal locality and skew

Temporal locality and data skew are two fundamental workload characteristics that describe how data is accessed in a distributed system.

They answer different questions:

- Temporal locality: Is data that was accessed recently likely to be accessed again soon?
- Skew: Are some keys accessed significantly more frequently than others?

Both properties strongly influence caching, partitioning, load balancing, state placement, and the performance of distributed dataflow systems.

## 1. Temporal locality

Temporal locality is the tendency for recently accessed data to be accessed again in the near future.

Consider a distributed system processing events associated with customer IDs.

An example access sequence:

```text
Time --->

A, B, A, C, A, B, A, C, B, A
```

Notice that the same keys are repeatedly accessed within a relatively short period.

This workload exhibits temporal locality.

Compare it with:

```text
Time --->

A, B, C, D, E, F, G, H, I, J
```

Here, every access targets a different key, with no reuse within the observed interval.

This sequence exhibits little temporal locality.

### Why does temporal locality exist?

Real-world systems frequently process related data close together in time.

Examples include:

- A popular video receiving thousands of interactions within minutes.
- A customer repeatedly interacting with an application during a session.
- A particular stock receiving many trades during a period of market activity.
- A database repeatedly executing queries over the same subset of records.
- A distributed query engine repeatedly accessing recently loaded data.

The underlying principle is that accesses are not always independent or uniformly random.

### The working set

Temporal locality is closely related to the concept of a working set.

A working set is the collection of distinct keys accessed within a given time window.

Suppose a stateful application maintains one million keys, but only 10,000 are accessed during the last minute.

```text
Total key space: 1,000,000 keys

+---------------------------------------+
|                                       |
|  Cold / inactive keys                 |
|                                       |
|      +-------------------------+      |
|      | Active working set      |      |
|      |                         |      |
|      | 10,000 keys             |      |
|      +-------------------------+      |
|                                       |
+---------------------------------------+
```

Only 1% of the accumulated key space is active in that window.

If the active keys continue to be accessed over subsequent windows, the workload has strong temporal locality.

This is important because the system can optimize for a much smaller working set than the total stored dataset.

### Temporal locality evolves

The working set is not necessarily fixed.

For example:

```text
Time T1:
  Hot keys: A, B, C

Time T2:
  Hot keys: A, B, D

Time T3:
  Hot keys: B, D, E

Time T4:
  Hot keys: D, E, F
```

The working set changes gradually.

Most active keys persist between consecutive time windows, even though some become cold and others become hot.

This pattern can be described as a slowly evolving working set.

It is particularly valuable for systems that move data toward the computation accessing it: recently fetched state is likely to be reused before becoming cold.

## 2. Data skew

Data skew occurs when workload or data is distributed unevenly across keys, partitions, or workers.

Consider an application processing one million events.

Suppose the events are distributed across four keys:

| Key | Events  | Percentage |
| --- | ------- | ---------- |
| A   | 700,000 | 70%        |
| B   | 200,000 | 20%        |
| C   | 70,000  | 7%         |
| D   | 30,000  | 3%         |

Key A receives significantly more traffic than the others.

This is a skewed workload.

### Uniform versus skewed distributions

Uniform workload:

```text
Key A: #################### 25%
Key B: #################### 25%
Key C: #################### 25%
Key D: #################### 25%
```

Skewed workload:

```text
Key A: ################################################## 70%
Key B: ##############                                     20%
Key C: #####                                               7%
Key D: ##                                                  3%
```

Skew creates an important problem in distributed systems: equal numbers of keys do not necessarily produce equal workloads.

### Skew and partitioning

Suppose four tasks process events using key-based partitioning.

```text
                 Incoming Events
                        |
                        v
                 Hash Partition
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
        Task A        Task B        Task C
        Key 1         Key 2         Key 3

        80K/s         10K/s         10K/s
```

Even if the partitioning scheme distributes keys evenly, it may distribute actual computational load poorly.

Task A becomes overloaded while Tasks B and C remain mostly idle.

The system may experience:

- Increased processing latency.
- Backpressure.
- Growing queues and backlog.
- CPU utilization imbalance.
- Reduced overall throughput.

Adding workers does not automatically solve skew. If one exceptionally hot key must be processed by a single owner, that key can remain a bottleneck.

### Skew is often modeled using Zipf's law

Many real-world workloads exhibit approximately Zipfian popularity distributions.

A common model assigns the probability of accessing the key of rank `i` as:

```text
P(i) = (1 / i^s) / sum(j = 1..N, 1 / j^s)
```

Where:

- `i` is the key's popularity rank.
- `N` is the total number of keys.
- `s` controls how skewed the distribution is.

When `s=0`, all keys are equally likely to be accessed.

As `s` increases, a small number of popular keys receive an increasingly large fraction of requests.

This is why caches, storage servers, and distributed processing tasks can experience heavily concentrated load even when keys are evenly partitioned.

## 3. Temporal locality versus skew

Although related, these properties describe different aspects of a workload.

| Property              | Temporal locality                              | Skew                                       |
| --------------------- | ---------------------------------------------- | ------------------------------------------ |
| Main question         | Will recently accessed keys be accessed again? | Are some keys more popular than others?    |
| Primary dimension     | Time                                           | Access frequency distribution              |
| Key concept           | Reuse and working-set evolution                | Unequal popularity                         |
| Main optimization     | Caching and lazy migration                     | Load balancing and partitioning            |
| Main risk when absent | Cache misses and repeated transfers            | More uniform load, often easier to balance |

They are not interchangeable.

A workload can exhibit strong temporal locality with little skew, or strong skew with rapidly changing hot keys.

### Example A: High temporal locality, low skew

Suppose 100 keys are active for an extended period.

Each active key receives approximately the same number of requests.

```text
Time T1: A B C D A B C D
Time T2: A B C D A B C D
Time T3: A B C D A B C D
```

Accesses repeatedly target the same working set.

Temporal locality is high, but popularity is uniformly distributed across the active keys.

### Example B: High skew, rapidly changing hot keys

```text
Time T1:
  A -> 90% of requests

Time T2:
  B -> 90% of requests

Time T3:
  C -> 90% of requests

Time T4:
  D -> 90% of requests
```

Each time interval is strongly skewed.

However, the identity of the hot key changes quickly.

There is little persistence in the hot working set across intervals.

The distinction matters because a system optimized around yesterday's hot keys may perform poorly when popularity shifts.

## 4. Why these properties matter for state reconfiguration

Consider a stateful distributed system maintaining 100 GB of application state.

A scaling operation assigns half its key space to newly created tasks.

With eager state migration, the system might need to move approximately 50 GB, assuming state is distributed evenly across the reassigned keys.

But consider a workload with strong temporal locality.

Only 2 GB of the reassigned state is actively accessed after the reconfiguration.

```text
                 Reconfiguration
                        |
             +----------+----------+
             |                     |
             v                     v
       Eager Migration       Lazy Migration
             |                     |
             v                     v
        Move 50 GB             Move 2 GB
             |                     |
             v                     v
       All reassigned         Only accessed
       state transferred      state transferred
```

The remaining 48 GB can stay where it is, provided the existing storage location remains available.

This is a direct consequence of temporal locality.

### What role does skew play?

Suppose 90% of the incoming events target 1% of the keys.

If those hot keys are reassigned during reconfiguration, fetching them once and keeping them local can benefit a large fraction of subsequent events.

Consider:

```text
                    Task B
                 (New Owner)
                      |
                      v
                  Key A used
                      |
                      v
               Fetch from Task A
                      |
                      v
                Store locally
                      |
                      v
              Future accesses local
```

For a very popular key, the initial remote transfer cost is amortized over many subsequent accesses.

However, skew also affects load distribution. Moving state efficiently does not by itself balance the workload. The system still needs an ownership assignment that distributes hot keys appropriately.

## 5. Why the combination is powerful

The strongest opportunity arises when the workload has both:

1. A relatively small active working set.
2. A high concentration of accesses within that working set.

Consider:

```text
Total state:       100 GB
Active state:        5 GB
Hot state:           1 GB

Access distribution:
  80% of events -> Hot state
  15% of events -> Other active state
   5% of events -> Remaining state
```

A system can potentially achieve three benefits.

Reduced migration: Most cold state never needs to move during ordinary scale-out or rebalancing.

High locality: Frequently accessed state is fetched once, then reused locally.

Better resource utilization: Ownership of hot keys can be redistributed to reduce overloaded tasks.

But the benefits depend on the stability of access patterns and the ability to repartition the workload.

## 6. Engineering considerations

### Temporal locality and cache hit rates

Caching benefits when recently accessed data is likely to be reused.

A cache stores a subset of the total dataset:

```text
               Incoming Request
                       |
                       v
                 +-----------+
                 | Cache     |
                 +-----------+
                  |         |
                Hit        Miss
                  |         |
                  v         v
               Return    Fetch from
               data      backing store
```

A small, stable working set can produce a high cache hit rate.

A rapidly changing working set may lead to repeated misses and evictions.

### Skew and hot partitions

A skewed workload can overload individual partitions.

```text
Worker A: 95% CPU
Worker B: 20% CPU
Worker C: 15% CPU
Worker D: 10% CPU
```

Possible mitigation strategies include hot-key-aware partitioning, dynamic rebalancing, splitting associative computations, or replicating read-only data where consistency semantics permit.

A single key requiring strictly sequential state updates remains a special challenge: merely adding workers cannot make its updates independently parallelizable.

### Measuring the properties

Useful temporal locality metrics include working-set size over time, repeat-access rate, cache hit rate, and overlap between consecutive working sets.

Useful skew metrics include per-key request frequency, top-K traffic concentration, per-partition utilization, and the distribution of processing costs.

These measurements serve different purposes: temporal-locality metrics help determine what state is worth keeping close, while skew metrics help determine where computation should be assigned.

## 7. Key insight

Temporal locality and skew should be considered together, but optimized differently.

```text
                    Workload
                       |
             +---------+---------+
             |                   |
             v                   v
      Temporal Locality         Skew
             |                   |
             v                   v
      Which keys are       Which keys consume
      likely to be         the most resources?
      reused soon?
             |                   |
             v                   v
      State placement      Load balancing
      Cache management     Key partitioning
      Lazy migration       Hot-key mitigation
```

Temporal locality tells a distributed system which data is worth keeping close to computation. Skew tells it where the computational pressure is concentrated.

Together, they provide the information needed to make intelligent decisions about state placement, migration, partitioning, and dynamic reconfiguration.
