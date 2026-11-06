# Workload-aware scheduling

The fundamental problem in distributed scheduling is that the unit of resource allocation is not necessarily the unit of useful work.

A cluster scheduler might allocate resources to individual processes, containers, or tasks. However, the application may require multiple tasks to execute together before it can make any progress.

This mismatch creates several difficult problems:

- Resources can be allocated successfully without producing useful work.
- Independently valid placement decisions can produce globally inefficient allocations.
- Competing workloads can block one another even when the cluster has available capacity.
- Fairness, utilization, and execution latency can require conflicting scheduling decisions.
- The optimal scheduling policy depends on the communication and synchronization requirements of the workload.

The central architectural principle is:

**Scheduling must understand the execution semantics of the workload, not merely the resource requirements of its individual tasks.**

## 1. The fundamental problem: local decisions versus global progress

Consider a distributed computation that requires four workers, each consuming one GPU.

The cluster contains eight GPUs, distributed across four machines.

```text
       CLUSTER
+-------------------+
| Node A: 2 GPUs    |
| Node B: 2 GPUs    |
| Node C: 2 GPUs    |
| Node D: 2 GPUs    |
+-------------------+

Job J:
    Worker 1 -> 1 GPU
    Worker 2 -> 1 GPU
    Worker 3 -> 1 GPU
    Worker 4 -> 1 GPU

Requirement:
    All 4 workers must execute together.
```

A traditional task-oriented scheduler evaluates each worker independently.

For each task, it asks:

> Is there a machine with sufficient resources to execute this task?

Suppose the cluster is already running other workloads, leaving only three GPUs available.

The scheduler might produce:

```text
                          Job J
                            |
    +---------------+-------+-------+---------------+
    |               |               |               |
    v               v               v               v
Worker 1        Worker 2        Worker 3        Worker 4
    |               |               |               |
    v               v               v               v
  GPU 1           GPU 2           GPU 3          PENDING


Allocated GPUs: 3
Useful progress: 0
```

Every individual placement decision is valid.

However, the overall job cannot execute because its fourth worker is missing.

The result is a pathological state:

- Three GPUs are allocated.
- The distributed computation makes no useful progress.
- Other jobs may be prevented from using those GPUs.
- The cluster reports allocated resources without corresponding productive execution.

This is a partial-allocation problem.

It demonstrates a crucial distinction:

```text
Resource allocation != Useful progress
```

For a rigid, synchronous distributed job requiring `N` workers, a simplified progress model is:

```text
P(k) = 0    if k < N
P(k) = P_N  if k = N
```

Where `k` is the number of available workers and `P_N` is the progress rate when all required workers are available.

This model does not apply to every distributed application. Elastic workloads may continue operating at reduced capacity. But it captures the fundamental challenge of tightly coupled jobs.

### Why independently scheduling tasks fails

The scheduler is optimizing a local objective:

```text
Can this task fit on this node?
```

The application requires a global property:

```text
Can the entire computation execute?
```

These objectives are not equivalent.

The same architectural problem appears in distributed query engines, parallel scientific computations, coordinated batch processing, and other systems with tightly coupled execution stages.

**Engineering lesson: The scheduling abstraction should match the smallest group of tasks that must make progress together.**

## 2. Choosing the correct unit of scheduling

Different execution models require different scheduling granularities.

| Scheduling unit | Main concern                             | Typical workload                 |
| --------------- | ---------------------------------------- | -------------------------------- |
| Individual task | Find a suitable execution location       | Independent batch tasks          |
| Process group   | Allocate coordinated resources           | Parallel scientific computing    |
| Job             | Start a complete distributed computation | Synchronous distributed training |
| Request         | Meet latency and capacity requirements   | Online inference                 |

Consider two different workloads.

Workload A: Independent tasks

```text
                  JOB
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
Task A          Task B          Task C
   |               |               |
   v               v               v
 DONE           RUNNING         WAITING
```

Task A can finish even if Task C has not started.

Partial allocation is beneficial because every completed task contributes useful work.

Workload B: Synchronized tasks

```text
                  JOB
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
Task A          Task B          Task C
   |               |               |
   +---------------+---------------+
                   |
                   v
                BARRIER
                   |
                   v
            NEXT ITERATION
```

Every iteration requires participation from all workers.

If one worker is missing, the others may block at the synchronization barrier.

This produces a fundamental tradeoff:

| Independent scheduling          | Coordinated scheduling                     |
| ------------------------------- | ------------------------------------------ |
| Simple, incremental placement   | More complex allocation decisions          |
| Works well for elastic tasks    | Works well for tightly coupled tasks       |
| Can utilize small resource gaps | May need to wait for a complete allocation |
| Risks partial-allocation waste  | Risks resource idleness while waiting      |
| Lower coordination overhead     | Higher coordination overhead               |

There is no universally optimal scheduling granularity.

**The correct choice depends on whether partial execution produces useful progress.**

## 3. Gang scheduling: treating a group of tasks as one allocation

**Gang scheduling solves the partial-allocation problem by requiring a collection of tasks to be admitted as a group.**

Instead of scheduling workers independently, the scheduler asks:

> Can the cluster satisfy the resource requirements of the entire job?

If the answer is no, the job remains queued.

```text
                 Job J
              (4 workers)
                   |
                   v
           +---------------+
           |   Admission   |
           |  Controller   |
           +---------------+
                   |
                   v
         Enough resources for
            all 4 workers?
                   |
   +---------------+---------------+
   |                               |
  NO                              YES
   |                               |
   v                               v
QUEUED                         ADMITTED
                                   |
                                   v
                            +-------------+
                            | Worker 1    |
                            | Worker 2    |
                            | Worker 3    |
                            | Worker 4    |
                            +-------------+
                                   |
                                   v
                                RUNNING
```

This changes the scheduler's behavior from incremental allocation to coordinated allocation.

### The tradeoff: avoiding waste versus delaying work

Suppose a cluster has eight GPUs, three of which are free.

Two jobs are waiting:

- Job A requires four GPUs.
- Job B requires two GPUs.

A strict FIFO scheduler might block Job B because Job A is first, even though Job B could execute immediately.

This is head-of-line blocking.

```text
Queue:
    [ Job A: 4 GPUs ] -> [ Job B: 2 GPUs ]

Cluster:
    Available: 3 GPUs

FIFO:
    Job A cannot start
    Job B waits behind A

    3 GPUs remain idle
```

An alternative is backfilling:

```text
Queue:
    [ Job A: 4 GPUs ] -> [ Job B: 2 GPUs ]

Cluster:
    Available: 3 GPUs

Backfilling:
    Job A remains queued
    Job B starts

    1 GPU remains idle
```

**Backfilling improves utilization but introduces another problem: a large job can starve if small jobs continuously consume newly available resources.**

A practical scheduler therefore needs a policy for protecting older or larger jobs, potentially using reservations, aging, or predicted completion times.

The key tradeoff:

```text
High utilization <-> Predictable waiting time
```

### Gang admission is not the same as atomic placement

There is an important distributed-systems subtlety.

A queue manager can determine that enough resources appear to exist, but the actual placement may occur later, through another component.

```text
Time T1:
    Queue manager observes 4 free GPUs

Time T2:
    Job J admitted

Time T3:
    Another allocation changes capacity

Time T4:
    Only 3 workers can be placed
```

The admission decision was correct relative to a snapshot, but that snapshot became stale.

**Gang scheduling therefore requires coordination between admission and placement.**

Possible mechanisms include reservation, scheduling gates, allocation ownership, and rollback or retry procedures.

**Engineering lesson: Admission guarantees are only as strong as the mechanism enforcing them at allocation time.**

## 4. Placement is a topology problem, not merely a capacity problem

Finding enough resources does not guarantee a good placement.

Consider a distributed computation where workers frequently exchange data.

Two placements are possible.

Placement A: Workers close together

```text
NODE 1
+--------------------+
| GPU 1 <----> GPU 2 |
|   |            |   |
| GPU 3 <----> GPU 4 |
+--------------------+

High-bandwidth local links
Low communication latency
```

Placement B: Workers spread across machines

```text
 Node A          Network        Node B
+-------+                      +-------+
| GPU 1 |--------------------->| GPU 3 |
| GPU 2 |<---------------------| GPU 4 |
+-------+                      +-------+

Network contention
Higher communication cost
```

Both placements satisfy the same GPU count.

But their execution performance can differ significantly.

For synchronized workloads, iteration time is approximately determined by the slowest participating worker or communication path:

```text
T_iteration ~= max_i(T_compute_i + T_communication_i) + T_coordination
```

This means placement decisions affect computation speed, not just resource utilization.

### The tradeoff: locality versus scheduling latency

There are two strategies:

First-fit placement: Start as soon as enough resources exist, regardless of whether the placement is ideal.

Topology-aware placement: Wait or search for resources with favorable communication characteristics.

| First-fit                            | Topology-aware                          |
| ------------------------------------ | --------------------------------------- |
| Usually starts sooner                | May wait longer                         |
| Easier to implement                  | Requires hardware-topology knowledge    |
| Greater placement flexibility        | More restrictive placement              |
| Can create communication bottlenecks | Can improve steady-state execution      |
| Often suitable for independent work  | Often suitable for tightly coupled work |

A useful objective is not simply to minimize queueing time:

```text
T_total = T_queue + T_execution
```

A job that waits 30 seconds for an efficient allocation may finish earlier than one that starts immediately but executes slowly.

**Engineering lesson: Optimize time-to-completion rather than treating resource allocation latency and execution performance independently.**

## 5. Queue management: deciding who gets to run

Scheduling becomes a multi-tenant resource-allocation problem when several teams or workloads compete for the same cluster.

Suppose the cluster contains 16 GPUs.

```text
               GPU CLUSTER
                 16 GPUs
                    |
    +---------------+---------------+
    |                               |
    v                               v
 Team A                          Team B
Quota: 8                        Quota: 8
```

If Team A is idle, allowing Team B to use only eight GPUs wastes half the cluster.

A more efficient policy permits borrowing and lending:

```text
 Team A                      Team B
Quota: 8                    Quota: 8
Using: 0                    Using: 16

     8 GPUs temporarily borrowed
    A ------------------------> B
```

But what happens when Team A submits a job requiring eight GPUs?

The scheduler must reclaim capacity.

That introduces several policy choices:

- Wait for completion: Avoid interrupting Team B, but increase Team A's waiting time.
- Preempt Team B: Restore capacity quickly, but potentially discard useful computation.
- Checkpoint and suspend: Preserve progress, but incur checkpointing, storage, and recovery overhead.

These policies optimize different objectives.

| Objective                  | Preferred behavior               |
| -------------------------- | -------------------------------- |
| Maximum utilization        | Aggressive borrowing             |
| Strong tenant isolation    | Strict quotas                    |
| Predictable access         | Reservations and bounded reclaim |
| Minimum wasted computation | Conservative preemption          |
| Low scheduling latency     | Flexible resource sharing        |

Importantly, **fairness must be defined over time, not merely over instantaneous resource allocation.**

A scheduler may also need to account for resource heterogeneity, historical usage, waiting time, and job priority.

**Engineering lesson: Fair scheduling is a policy problem that must be separated from low-level resource placement.**

## 6. Request-level scheduling introduces a different problem

Distributed training typically allocates resources to jobs that execute for extended periods.

Online inference operates differently.

Its scheduling unit is often a request, and requests can have highly variable execution costs.

```text
               REQUESTS
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
 Short          Medium           Long
Request         Request         Request
   |               |               |
   +---------------+---------------+
                   |
                   v
           REQUEST SCHEDULER
                   |
                   v
             GPU EXECUTORS
```

Two requests that appear identical from a resource-allocation perspective may require very different amounts of computation and memory.

The scheduler must consider:

- Available processing capacity.
- Request latency deadlines.
- Queued and currently executing work.
- Memory required for request state.
- Opportunities to batch compatible requests.
- Locality of already cached state.

For stateful inference, moving a request between executors may require reconstructing or transferring intermediate state.

Consequently, scheduling is no longer solely about where to place a worker. It is also about which request should execute next, whether it should be batched with others, and whether the selected executor can meet its latency objective.

### Throughput versus latency

Batching requests may improve accelerator utilization:

```text
Without batching:

Request A -> GPU
Request B -> GPU
Request C -> GPU

With batching:

[ A + B + C ] -> GPU
```

However, waiting for more requests to form a batch increases queueing latency.

The scheduler therefore balances:

```text
Throughput <-> Tail latency
```

At high utilization, queueing delay can increase sharply, even when the underlying execution engine is functioning correctly.

This is especially important for systems with strict latency SLOs.

**Engineering lesson: Long-running job scheduling and latency-sensitive request scheduling require different control loops and admission policies.**

## 7. Why scheduling should be a layered architecture

A single scheduler responsible for workflows, fairness, resource accounting, topology, and request execution becomes difficult to reason about.

A better architecture separates decisions according to their scope.

```text
          WORKFLOW
              |
              v
+---------------------------+
| Workflow Controller       |
|                           |
| What work should run?     |
| When is it ready?         |
+---------------------------+
              |
              v
+---------------------------+
| Queue / Admission Manager |
|                           |
| Which jobs may start?     |
| Who gets capacity?        |
| Are quotas satisfied?     |
+---------------------------+
              |
              v
+---------------------------+
| Placement Scheduler       |
|                           |
| Which nodes are suitable? |
| Where should tasks run?   |
+---------------------------+
              |
              v
+---------------------------+
| Resource Management       |
|                           |
| Which devices exist?      |
| Which are allocatable?    |
+---------------------------+
              |
              v
          EXECUTION
```

These layers manage different constraints and often operate at different timescales.

For example, a workflow controller may react to the completion of an upstream job. A queue manager decides whether the next job is entitled to resources. A placement scheduler selects nodes, while lower-level resource mechanisms expose and allocate suitable devices.

### The tradeoff: separation of concerns versus coordination complexity

Layering provides modularity:

- Different scheduling policies can evolve independently.
- Admission control can be shared across workload types.
- Placement logic can remain focused on cluster topology.
- Resource management can specialize in hardware details.

But it also introduces coordination problems.

Suppose the admission manager believes a job has been accepted, while the placement scheduler cannot satisfy its requirements.

The system needs an explicit reconciliation protocol.

```text
Admission Manager                      Placement Scheduler
        |                                       |
        |------------- Admit Job -------------->|
        |                                       |
        |<---------- Placement Failed ----------|
        |                                       |
        |---------- Retry / Requeue ----------->|
        |                                       |
```

This creates requirements for durable job state, idempotent operations, timeouts, cancellation, and resource reclamation.

A robust implementation should distinguish states such as:

```text
                SUBMITTED
                    |
                    v
                 QUEUED
                    |
                    v
                ADMITTED
                    |
                    v
                 PLACING
                    |
    +---------------+---------------+
    |                               |
    v                               v
 RUNNING                    PLACEMENT_FAILED
    |                               |
    v                               v
COMPLETED                       REQUEUED
```

**An admitted job is not necessarily running.**

Conflating these states can produce resource leaks, inaccurate accounting, or jobs that remain indefinitely stuck.

**Engineering lesson: When admission and placement are separate decisions, resource ownership and state transitions must be explicit.**

## 8. Important failure modes and engineering practices

Several recurring problems emerge from these scheduling models.

| Failure mode              | Root cause                                        | Engineering practice                               |
| ------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| Partial allocation        | Independent task scheduling for coupled jobs      | Gang scheduling or coordinated admission           |
| Head-of-line blocking     | Strict ordering with heterogeneous job sizes      | Backfilling with starvation protection             |
| Resource fragmentation    | Allocations leave unusable capacity combinations  | Topology-aware placement and reservations          |
| Tenant starvation         | Unbounded resource borrowing                      | Quotas, aging, and reclaim policies                |
| Poor job performance      | Placement ignores communication topology          | Network- and locality-aware scoring                |
| Stale admission decisions | Resource availability changes between controllers | Reservation, revalidation, and reconciliation      |
| Scheduling instability    | Repeated preemption and rescheduling              | Hysteresis, cooldowns, and bounded retries         |
| Excessive request latency | Admission exceeds executable capacity             | Queue bounds, admission control, and load shedding |

An additional subtlety is that the scheduler operates with an imperfect view of the cluster.

Resource availability, device health, network conditions, and task execution state are continuously changing.

**Therefore, scheduling is not a one-time optimization problem. It is a continuous control and reconciliation problem.**

A practical scheduler must both make good initial decisions and recover when those decisions become invalid.

## 9. The architectural principles

The broader lessons generalize beyond accelerator workloads.

1. **Match allocation granularity to execution semantics.** Independent tasks benefit from incremental placement. Synchronized tasks require coordinated allocation.

2. **Distinguish capacity from useful capacity.** A cluster may have free resources that cannot satisfy the topology, memory, or group-size requirements of a waiting job.

3. **Separate admission from placement.** Admission determines whether work should consume resources; placement determines which specific resources it should consume. The two decisions must remain consistent.

4. **Treat scheduling as a global optimization problem.** Individually valid task placements do not necessarily produce good cluster-wide outcomes.

5. **Make progress the primary optimization objective.** Allocated CPU or GPU time is a poor proxy for useful work when tasks can block on synchronization or communication.

6. **Design for imperfect information and failures.** Every scheduling decision may be invalidated by a concurrent allocation, node failure, changing workload, or stale state.

7. **Explicitly choose between competing objectives.** Utilization, fairness, locality, latency, and predictability cannot always be maximized simultaneously.

## Final perspective

**The most important conceptual shift is from resource-centric scheduling to workload-aware scheduling.**

A resource-centric scheduler asks:

```text
"Where can this task run?"
```

A workload-aware scheduler asks:

```text
"What must be true for this computation
       to make useful progress?"

                   |
                   v

  "Which resources must be available
           simultaneously?"

                   |
                   v

   "Which allocation minimizes total
  completion time and interference?"

                   |
                   v

 "How can the allocation remain fair,
     efficient, and recoverable?"
```

**The deeper distributed-systems lesson is that scheduling is not merely task placement. It is the coordination of resource ownership, execution dependencies, admission policies, and progress guarantees across a dynamic cluster.**
