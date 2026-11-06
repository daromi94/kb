# Pipelined DAG execution

The fundamental problem is that traditional DAG execution engines often introduce synchronization barriers between stages that exchange data.

These barriers simplify scheduling, fault tolerance, and resource management, but they also prevent downstream computations from making progress while upstream computations are still producing data.

Pipelined execution removes this restriction by allowing dependent stages to execute concurrently and exchange intermediate results incrementally.

However, this changes several fundamental properties of the system:

- Scheduling becomes a resource coordination problem.
- Intermediate data becomes transient rather than materialized.
- Backpressure must propagate across stage boundaries.
- Failure recovery becomes more tightly coupled.
- Resource consumption increases because producers and consumers coexist.

The central architectural trade-off is:

**Materialization provides execution independence and fault isolation. Pipelining provides lower latency and continuous data flow at the cost of tighter coordination.**

## 1. The problem: shuffles create synchronization barriers

Consider a distributed computation with three logical operations:

```text
   Input data
        |
        v
+---------------+
|    Stage A    |
| Read + Filter |
+---------------+
        |
        v
+---------------+
|    Stage B    |
|  Repartition  |
|    by key     |
+---------------+
        |
        v
+---------------+
|    Stage C    |
|   Aggregate   |
+---------------+
        |
        v
     Results
```

In distributed data processing, records with the same key often need to be processed by the same downstream task.

For example, suppose a system aggregates events by `user_id`.

Initially, events are distributed across three workers:

```text
Worker 1          Worker 2          Worker 3
--------          --------          --------
(A, 10)           (B, 20)           (A, 30)
(C, 15)           (A, 40)           (C, 25)
(B,  5)           (C, 10)           (B, 50)
```

To aggregate correctly, the engine must redistribute records so that every record for a particular key reaches its assigned consumer.

```text
Producers                                   Consumers

Worker 1 -----+                         +----> Key A
              |                         |
Worker 2 -----+------- Shuffle -------->+----> Key B
              |                         |
Worker 3 -----+                         +----> Key C
```

This is an all-to-all communication pattern: every producer may need to send data to every consumer.

The shuffle is necessary because data ownership changes between stages.

The problem isn't the redistribution itself. The problem is how the execution engine coordinates the two stages around that redistribution.

### Traditional approach: blocking shuffle

A traditional blocking shuffle works approximately as follows:

```text
       STAGE A
+-------------------+
|  Producer Task 1  |
|  Producer Task 2  |
|  Producer Task 3  |
+-------------------+
          |
          v
+-------------------+
|    Materialize    |
| intermediate data |
+-------------------+
          |
          v
       BARRIER
All producers finish
          |
          v
       STAGE B
+-------------------+
|  Consumer Task 1  |
|  Consumer Task 2  |
|  Consumer Task 3  |
+-------------------+
```

The scheduler waits until the producer stage has completed before scheduling the downstream stage.

This provides several useful properties.

First, execution independence. Producer tasks can finish and release their execution resources before consumers begin.

Second, recoverability. Intermediate data can be retained and reread. If a consumer fails, the system can often restart that consumer without repeating the entire upstream computation.

Third, scheduling flexibility. The cluster does not need enough capacity to execute every stage simultaneously.

But consider a producer that runs for 30 seconds and a consumer that requires 20 seconds.

With sequential execution:

```text
Time ---------------------------------------------------------->

Stage A: [======== 30 seconds =========]

Stage B:                               [======= 20s =======]

Total:                                            50 seconds
```

Even if Stage A starts producing useful records after one second, Stage B cannot begin processing those records until the entire producer stage completes.

For finite workloads, this introduces unnecessary latency. For continuously running workloads, it is fundamentally incompatible with a downstream stage that waits for a producer to finish, because that producer may never finish.

## 2. Pipelined shuffle: replace the barrier with continuous data exchange

A pipelined shuffle changes the dependency from:

```text
Producer completes
         |
         v
  Consumer starts
```

to:

```text
     Producer starts
            |
            v
     Consumer starts
            |
            v
Both execute concurrently
```

**The key difference is that consumers can read intermediate results while producers are still computing them.**

### Architecture

```text
                      DAG Scheduler
                            |
                            v
                    Start both stages
                            |
      +---------------------+---------------------+
      |                                           |
      v                                           v

  PRODUCERS                                   CONSUMERS

+----------+                                +----------+
| Task A1  |----------------+-------------->| Task B1  |
+----------+                |               +----------+
                            |
+----------+                |               +----------+
| Task A2  |----------------+-------------->| Task B2  |
+----------+                |               +----------+
                            |
+----------+                |               +----------+
| Task A3  |----------------+-------------->| Task B3  |
+----------+                                +----------+

              Incremental network transfer
```

Each producer performs its computation, determines the appropriate destination for each record, and transfers buffered records to the relevant consumer.

The consumer can begin processing as soon as data arrives.

Importantly, **pipelining does not eliminate the shuffle.** Repartitioning, serialization, network transfer, and deserialization are still necessary.

It eliminates the requirement that the complete producer stage finish before downstream computation begins.

### Latency implications

With pipelining, the execution timeline becomes:

```text
Time ------------------------------------------------>

Stage A: [======== 30 seconds =========]
Stage B:           [=== 20 seconds ====]

         ^         ^
         |         |
         |         | Consumer begins receiving records
         |
         | Producer begins executing
```

For a streaming-compatible workload, end-to-end processing of individual records can overlap substantially.

For finite workloads, an idealized comparison is:

```text
T_blocking ~= T_A + T_B
```

```text
T_pipelined ~= max(T_A, T_B) + T_pipeline_overhead
```

This is only an approximation. Actual execution depends on producer and consumer rates, startup costs, data dependencies, and buffering.

**The greatest benefit often isn't reduced total computation time. It is reduced time from producing a record to processing that record downstream.**

### An important distinction: pipelining versus parallelism

**Parallelism means multiple tasks execute at the same time.**

**Pipelining means downstream processing overlaps with upstream processing.**

A traditional distributed execution engine may already have substantial task parallelism within a stage:

```text
Stage A
+--------+  +--------+  +--------+
| Task 1 |  | Task 2 |  | Task 3 |
+--------+  +--------+  +--------+

BARRIER

Stage B
+--------+  +--------+  +--------+
| Task 4 |  | Task 5 |  | Task 6 |
+--------+  +--------+  +--------+
```

Pipelining introduces another dimension of concurrency: inter-stage parallelism.

The two forms of parallelism complement each other, but inter-stage concurrency consumes resources that sequential scheduling could otherwise reuse.

## 3. Concurrent DAG scheduling: why starting stages together is difficult

Changing the data-transfer mechanism is not sufficient.

Even if consumers can read data incrementally, the system cannot benefit from pipelining if its scheduler continues enforcing traditional stage-completion barriers.

This creates a second architectural requirement:

**The scheduler must understand that certain dependent stages form a concurrent execution group.**

### The resource deadlock problem

Suppose a cluster has four available task slots.

A pipelined computation requires three producer tasks and three consumer tasks.

```text
Cluster capacity: 4 task slots

Required:
  Stage A: 3 producers
  Stage B: 3 consumers

Total concurrent demand: 6 slots
```

Imagine the scheduler admits tasks opportunistically:

```text
+-------------------------------------+
|               CLUSTER               |
|                                     |
| Slot 1: Consumer B1                 |
| Slot 2: Consumer B2                 |
| Slot 3: Consumer B3                 |
| Slot 4: Producer A1                 |
|                                     |
+-------------------------------------+

Waiting for slots:
  Producer A2
  Producer A3
```

The consumers need data from all producers to complete their work.

But two producers cannot start because the consumers occupy the available slots.

```text
    Consumers
        |
        | Waiting for remaining producers
        v
Producers A2, A3
        |
        | Waiting for available slots
        v
    Consumers
```

This creates a resource deadlock.

Unlike traditional execution, where the scheduler can finish one stage and reuse its slots, the concurrent execution model requires sufficient simultaneous capacity.

### Solution: coordinated admission (gang scheduling)

A common approach is to treat connected stages as a scheduling group.

```text
               DAG Scheduler
                     |
                     v
          +--------------------+
          |  Pipelined Group   |
          |                    |
          |  Stage A: 3 tasks  |
          |  Stage B: 3 tasks  |
          +--------------------+
                     |
                     v
            Resource Admission
                     |
               Need 6 slots
                     |
     +---------------+---------------+
     |                               |
     v                               v
  Enough?                       Not enough
     |                               |
     v                               v
Admit group                    Reject / Wait
```

The group should only begin executing when sufficient resources can be allocated to make progress.

A concrete implementation may choose fail-fast admission rather than indefinite waiting to avoid a partially admitted group holding resources forever.

This introduces a fundamental trade-off.

**Sequential scheduling optimizes resource reuse. Concurrent scheduling optimizes overlap between dependent computations.**

Sequential execution can run a large DAG on a relatively small cluster by reusing execution capacity. Pipelined execution requires enough resources for producers and consumers to coexist.

This means a pipelined computation may experience lower latency but higher instantaneous resource consumption.

It also complicates elastic scaling, multi-tenant admission control, and fairness. Changes in cluster capacity can invalidate assumptions about whether a group fits.

The broader engineering lesson is that data dependencies and resource dependencies must be considered together. **A valid DAG does not necessarily imply a schedulable DAG.**

## 4. Backpressure becomes essential

Once stages execute concurrently, the rate at which producers generate data may differ from the rate at which consumers process it.

Consider:

```text
Producer throughput:  100,000 records/sec
Consumer throughput:   60,000 records/sec

Excess:                40,000 records/sec
```

Without flow control, intermediate buffers accumulate.

```text
      Producer
          |
          | 100K records/sec
          v
+------------------+
| Network / Queue  | ---> Growing memory consumption
+------------------+
          |
          | 60K records/sec
          v
      Consumer
```

For an unbounded stream, persistent growth of this kind eventually exhausts memory.

Pipelined shuffles therefore need backpressure that propagates across the network and into the upstream computation.

```text
   Producer
       |
       v
+-------------+
| Send Buffer |
+-------------+
       |
       v
    Network
       |
       v
+-------------+
| Read Buffer |
+-------------+
       |
       v
   Consumer

When consumer slows:

     Consumer slows
            |
            v
    Read buffer fills
            |
            v
  Network flow control
            |
            v
    Send buffer fills
            |
            v
Producer blocks or slows
```

A practical design combines bounded reader buffers, transport-level flow control, and bounded in-flight writer buffers. This can propagate pressure all the way back to the producer's input iterator.

There is an important distinction here: backpressure is not the same as admission control.

**Admission control determines whether a pipelined computation can start. Backpressure regulates how quickly data moves through an already-running computation.**

Both are needed.

### The buffering trade-off

Larger buffers allow better batching and network efficiency, but increase latency before partially filled buffers are sent.

Smaller buffers reduce waiting time but increase per-message overhead, including serialization, framing, network processing, and CPU work.

A useful strategy is to flush a buffer when either a size threshold or an age threshold is reached.

```text
        Buffer accumulates records
                     |
                     v
             +---------------+
             | Size reached? |
             +---------------+
                     |
 +-------------------+-------------------+
 |                                       |
Yes                                     No
 |                                       |
 |                               +---------------+
 |                               | Time expired? |
 |                               +---------------+
 |                                       |
 |                           +-----------+-----------+
 |                           |                       |
 |                          Yes                     No
 |                           |                       |
 +-------------+-------------+                       |
               |                                     |
               v                                     v
             SEND                                Continue
                                                 buffering
```

The engineering principle is to **use bounded buffering as a mechanism for smoothing short-term rate differences, not as a substitute for rate control.**

Sustained downstream saturation must eventually slow upstream work, shed work under an explicit policy, or obtain additional capacity.

## 5. Failure recovery: the hidden cost of removing materialization

This is arguably the most significant architectural trade-off.

Traditional blocking shuffles create an intermediate recovery boundary.

```text
         Stage A
            |
            v
+----------------------+
| Materialized Output  |
+----------------------+
            |
            v
         Stage B
```

Suppose Stage B fails.

If Stage A's intermediate output remains available, Stage B can be retried independently.

```text
Stage A: SUCCESS
Shuffle: AVAILABLE
Stage B: FAILED
            |
            v
      Retry Stage B
```

This is possible because the shuffle output has an independent lifetime from the producer task.

Pipelined shuffle removes that independence.

```text
Stage A -----------------> Stage B
        Transient stream      |
                              |
                              X
                        Stage B fails
```

Stage B may already have consumed a large portion of the stream, but Stage A has not retained a complete, independently replayable copy of those records.

Simply restarting Stage B would lose data unless the system provides another replay mechanism.

The natural recovery unit becomes the entire connected group.

```text
+--------------------------------+
|         Pipelined Group        |
|                                |
| Stage A ---> Stage B           |
|                 |              |
|                 X FAILURE      |
+--------------------------------+
                 |
                 v
            Abort group
                 |
                 v
      Restart from replayable
        input / checkpoint
```

This is group-atomic failure recovery: the stages execute together and, when necessary, fail together.

### Why this matters

A failure in a single consumer can force the recomputation of upstream work that would otherwise have been reusable.

Pipelining therefore reduces latency by weakening the isolation between stages.

**Materialization is not merely a storage operation. It is also a failure-containment mechanism.**

There is another subtle issue: a consumer may finish its local work before the producer has conclusively succeeded. The system must not expose final success prematurely. Otherwise, a late producer failure could invalidate data already treated as complete.

**This requires coordinated completion, not just coordinated scheduling.**

For stateful computations, durable checkpoints and replayable inputs can provide recovery. However, **exactly-once results additionally require appropriate state-restoration and output-commit semantics; pipelining alone does not guarantee them.**

## 6. The central trade-offs

| Dimension         | Blocking shuffle                               | Pipelined shuffle                         |
| ----------------- | ---------------------------------------------- | ----------------------------------------- |
| Latency           | Waits for stage completion                     | Incremental downstream processing         |
| Execution         | Stages execute sequentially across the shuffle | Stages overlap                            |
| Intermediate data | Materialized for reuse                         | Transient                                 |
| Memory            | Can rely on storage/spilling                   | Needs bounded in-flight buffers           |
| Resource demand   | Capacity can be reused between stages          | Concurrent capacity required              |
| Recovery          | Often localized to failed tasks or stages      | May require group replay                  |
| Backpressure      | Less tightly coupled across the shuffle        | Must propagate across stages              |
| Throughput        | Efficient for large batch processing           | May sacrifice peak throughput for latency |

Neither model is universally superior.

### When blocking execution is preferable

Blocking execution is attractive when throughput matters more than immediate results, intermediate results are expensive to recompute, resources are constrained, or the DAG needs independent stage retries.

It is particularly effective for large batch computations where throughput-oriented batching and flexible scheduling outweigh the cost of waiting at shuffle boundaries.

### When pipelined execution is preferable

Pipelining is attractive when records should be processed continuously, end-to-end latency matters, and intermediate data does not need to be independently retained.

It works especially well when the system has replayable inputs, a clear recovery strategy, and sufficient resources to execute dependent stages together.

A critical caveat is that concurrency does not automatically make every operator produce earlier final results. For example, a global aggregation still needs to know when all relevant inputs are complete before its final result is correct. **Pipelining improves incremental processing, but it cannot remove the semantic barriers inherent in the computation.**

## 7. Broader engineering lessons

### Lesson A: A DAG describes dependencies, not necessarily execution order

A logical dependency:

```text
A ---> B
```

does not necessarily mean that A must finish before B can begin.

It means B depends on A's output.

**Whether that dependency requires full materialization or supports incremental consumption is a separate architectural decision.**

This distinction allows the execution engine to separate the logical DAG from the execution contract of each edge.

### Lesson B: The exchange mechanism and scheduler must evolve together

Supporting a streaming transport without concurrent scheduling has limited value.

Similarly, scheduling stages concurrently without flow-controlled, incrementally readable exchanges is insufficient.

**The execution model requires cooperation between the scheduler, network transport, memory manager, and recovery mechanisms.**

A useful architectural separation is:

```text
     CONTROL PLANE
+--------------------+
| DAG dependencies   |
| Group scheduling   |
| Resource admission |
| Failure handling   |
+--------------------+
           |
           v
      DATA PLANE
+--------------------+
| Partition routing  |
| Serialization      |
| Network transfer   |
| Buffer management  |
| Backpressure       |
+--------------------+
```

The dependency type can define whether an edge is blocking or pipelined, while the corresponding exchange implementation handles actual data transfer.

This separation makes it possible to evolve execution strategies without hardcoding workload-specific behavior into every scheduler operation.

### Lesson C: Removing a synchronization barrier transfers complexity elsewhere

Blocking shuffle concentrates synchronization at the stage boundary.

**Pipelining moves the synchronization problem into runtime coordination, resource admission, flow control, and recovery.**

The barrier disappears from the normal execution path, but the system still needs mechanisms that preserve correctness.

### Lesson D: Choose recovery boundaries deliberately

**A materialized intermediate result is effectively a recovery boundary.**

Removing that boundary reduces storage and latency costs, but expands the scope of recomputation.

A useful design question is therefore not simply whether an intermediate result can be streamed.

It is whether the value of lower latency exceeds the cost of losing an independently recoverable intermediate result.

### Lesson E: Optimize for the relevant performance metric

Pipelined execution may improve per-record latency while reducing batch efficiency.

Small buffers, more simultaneous tasks, resource coordination, and tighter backpressure can all increase overhead.

**Optimizing time-to-first-result, P99 end-to-end latency, and maximum throughput can lead to different architectural choices.**

## Final architectural perspective

The broader design space can be summarized as follows:

```text
            DISTRIBUTED DAG
                   |
                   v
            Data dependency
                   |
     +-------------+-------------+
     |                           |
     v                           v
 BLOCKING                    PIPELINED
     |                           |
     v                           v
Materialize                 Stream data
     |                           |
     v                           v
Independent                 Concurrent
scheduling                  scheduling
     |                           |
     v                           v
Stage-local                 Coordinated
 recovery                    recovery
     |                           |
     v                           v
 Resource                    Resource
   reuse                   co-residency
```

**The most important takeaway is that pipelined execution is not merely a faster shuffle implementation. It is a different execution and recovery model for a distributed DAG.**

The design trades the independence provided by materialization for the latency advantages of continuous, concurrent computation.
