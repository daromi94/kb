# Meta's workload-aware CPU scheduling

## 1. The fundamental problem

A general-purpose operating system manages computational resources without fully understanding the purpose of the computations it executes.

The Linux kernel understands threads, CPU utilization, scheduling priorities, CPU topology and memory locality. However, it does not inherently understand application-level concepts such as request deadlines, critical paths, execution dependencies or the relative importance of different computations.

This creates a **semantic gap between the application and the operating system**.

```text
            Application
+---------------------------------+
| Request deadlines               |
| Execution dependencies          |
| Critical paths                  |
| Workload importance             |
+---------------------------------+
                 |
                 | Semantic gap
                 v
           Linux kernel
+---------------------------------+
| Runnable threads                |
| Scheduling weights              |
| CPU availability                |
| CPU topology                    |
+---------------------------------+
                 |
                 v
             Hardware
```

The application understands the purpose of the work. The kernel controls the resources necessary to execute it.

Historically, applications have had relatively limited mechanisms for communicating their execution requirements to the CPU scheduler.

Meta's approach uses `sched_ext`, an extensible Linux scheduling framework, to incorporate application-specific knowledge directly into CPU scheduling decisions.

The underlying principle is that **not all computational work has the same value at a particular point in time, even when it requires the same amount of CPU resources.**

## 2. What does a CPU scheduler actually do?

A machine typically has more threads than available logical CPUs. Therefore, the operating system must multiplex CPU resources among competing threads.

A thread can be in three conceptual execution states:

```text
             Wake-up
+---------+          +----------+
| Blocked | -------->| Runnable |
+---------+          +----------+
     ^                  |     ^
     |         Dispatch |     | Preemption
     |                  v     |
     |               +----------+
     +---------------| Running  |
Blocking operation   +----------+
```

- **Blocked:** Waiting for an event, such as I/O completion or lock acquisition.
- **Runnable:** Ready to execute but potentially waiting for CPU time.
- **Running:** Currently executing on a CPU.

When multiple threads become runnable, the scheduler must decide which thread executes, on which CPU, for how long, and under what conditions it should be preempted or migrated.

```text
Runnable threads

[T1] [T2] [T3] [T4] [T5] [T6]
              |
              v
    +-------------------+
    | Scheduler         |
    +-------------------+
              |
        +-----+-----+
        |           |
        v           v
    +-------+   +-------+
    | CPU 0 |   | CPU 1 |
    | T2    |   | T4    |
    +-------+   +-------+
```

**CPU scheduling is fundamentally a resource allocation and queueing problem.**

Its decisions influence latency, throughput, fairness, resource utilization, cache efficiency and power consumption.

## 3. Execution time versus scheduling latency

Consider a thread that needs to perform 1 ms of computation after receiving a network response.

The thread becomes runnable, but every CPU is currently executing other work.

```text
Network response arrives
            |
            v
 Thread becomes runnable
            |
            |<---------------- 5 ms --------------->|<-1 ms>|
            +---------------------------------------+-------+
                  Waiting for CPU                   | Execution
                                                    ^
                                                    |
                                            Thread dispatched
```

Although the computation requires only 1 ms of CPU time, its elapsed completion time is 6 ms.

Two different quantities are involved:

- **Service time:** Time spent actually executing.
- **Scheduling latency:** Time spent runnable but waiting for execution.

For a simplified CPU-only operation:

```text
T_completion = T_waiting + T_execution
```

Optimizing the algorithm reduces execution time. Optimizing the scheduler can reduce waiting time.

This distinction is important because many performance investigations focus exclusively on making computations faster, even when the dominant problem is the time spent waiting for resources.

A thread that spends 80% of its elapsed time waiting for CPU availability cannot achieve a large end-to-end improvement through computational optimization alone.

## 4. Why general-purpose CPU scheduling is insufficient

Linux's general-purpose fair schedulers are designed to support diverse workloads.

Historically, Linux used the Completely Fair Scheduler (CFS). Beginning with Linux 6.6, the fair scheduling class transitioned toward Earliest Eligible Virtual Deadline First (EEVDF).

### Completely Fair Scheduler (CFS)

CFS uses the concept of virtual runtime to approximate proportional CPU sharing.

For three equally weighted, continuously runnable threads competing for one CPU:

```text
Thread A: 33.3% of CPU capacity
Thread B: 33.3% of CPU capacity
Thread C: 33.3% of CPU capacity
```

Virtual runtime tracks weighted CPU consumption. A thread that has received relatively little CPU time becomes a stronger candidate for execution.

The objective is fair resource allocation.

### Earliest Eligible Virtual Deadline First (EEVDF)

EEVDF considers whether a thread has received its entitled share of CPU time and uses virtual deadlines to select among eligible threads.

```text
    Runnable threads
            |
            v
+-----------------------+
| Eligibility check     |
+-----------------------+
            |
            v
+-----------------------+
| Eligible threads      |
+-----------------------+
            |
            v
Earliest virtual deadline
            |
            v
        Execution
```

However, a virtual scheduling deadline is not the same as an application request deadline.

| Property                                   | CFS             | EEVDF                     |
| ------------------------------------------ | --------------- | ------------------------- |
| Proportional CPU fairness                  | Yes             | Yes                       |
| Primary selection mechanism                | Virtual runtime | Eligible virtual deadline |
| Application request awareness              | Not inherent    | Not inherent              |
| Distributed execution dependency awareness | No              | No                        |
| Application-specific importance            | Not inherent    | Not inherent              |

Both schedulers address a general-purpose resource allocation problem.

The limitation is not that they are poorly designed. It is that **they optimize using information that is incomplete from the application's perspective.**

## 5. CPU fairness does not necessarily produce optimal application performance

Imagine two equally weighted threads competing for CPU time.

Thread A performs computation needed to complete an active request. Thread B performs background maintenance.

Each requires 4 ms of CPU time.

Under an illustrative interleaved schedule:

```text
Time:  0   1   2   3   4   5   6   7   8 ms
       | B | A | B | A | B | A | B | A |
                                       ^
                                       |
                               Request completes
```

Under a critical-path-oriented schedule:

```text
Time:  0   1   2   3   4   5   6   7   8 ms
       | A | A | A | A | B | B | B | B |
                       ^
                       |
               Request completes
```

Both schedules perform the same amount of computational work.

| Metric                  | Interleaved | Critical-path first |
| ----------------------- | ----------- | ------------------- |
| CPU time allocated to A | 4 ms        | 4 ms                |
| CPU time allocated to B | 4 ms        | 4 ms                |
| Total completion time   | 8 ms        | 8 ms                |
| Request latency         | 8 ms        | 4 ms                |

Request latency has been reduced by 50% without increasing CPU capacity or making the computation faster.

The improvement comes entirely from changing the execution order.

This illustrates a fundamental scheduling principle:

**When work has different latency sensitivities, scheduling order becomes a performance optimization mechanism.**

CFS and EEVDF attempt to balance fairness and responsiveness, but neither automatically knows which application computations advance a particular request.

## 6. Why this matters in distributed systems

Consider a simplified retrieval and ranking system.

```text
                     Request
                        |
                        v
              +-------------------+
              | Request handler   |
              +-------------------+
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
+-------------+  +-------------+  +-------------+
| Retrieval   |  | Retrieval   |  | Retrieval   |
| Worker A    |  | Worker B    |  | Worker C    |
+-------------+  +-------------+  +-------------+
       |                |                |
       +----------------+----------------+
                        |
                        v
              +-------------------+
              | Aggregation       |
              +-------------------+
                        |
                        v
              +-------------------+
              | Ranking           |
              +-------------------+
                        |
                        v
                    Response
```

Each worker runs on a machine where application threads compete for CPU resources.

Suppose the aggregation stage requires all three retrieval results.

```text
Worker A: |=====|                       5 ms
Worker B: |=======|                     7 ms
Worker C: |....................=====|  25 ms

          . = Waiting for CPU
          = = Execution
```

Worker C performs only 5 ms of computation but experiences 20 ms of scheduling delay.

The entire request must wait for it.

For a parallel stage with a synchronization barrier:

```text
T_stage = max(T_1, T_2, ..., T_n)
```

The slowest participant determines when the next stage can begin.

This is known as **tail latency amplification**.

A local scheduling decision made by one kernel can delay a computation involving multiple machines.

Consequently, the operating system scheduler is not merely a local resource manager. It is indirectly part of the distributed execution engine.

## 7. Latency as a computational budget

Meta's ads-serving workload has another important characteristic: completing more computation within a fixed latency budget can improve the quality of the result.

An illustrative request has a deadline of 100 ms.

```text
Scenario A:
Retrieval (20 ms) --> Ranking (70 ms) --> Response (10 ms)

Scenario B:
Retrieval (40 ms) --> Ranking (50 ms) --> Response (10 ms)
```

Both requests finish within the deadline.

However, the second request has 20 ms less available for ranking candidate advertisements.

| Metric                 | Scenario A | Scenario B |
| ---------------------- | ---------- | ---------- |
| Retrieval latency      | 20 ms      | 40 ms      |
| Ranking budget         | 70 ms      | 50 ms      |
| Response latency       | 100 ms     | 100 ms     |
| Potential ranking work | Higher     | Lower      |

This introduces a different performance optimization objective.

Instead of exclusively minimizing response latency, the system can attempt to **maximize the amount of useful computation performed within a latency constraint**.

This pattern also appears in search engines, recommendation systems, distributed query engines, real-time inference and optimization algorithms.

Latency improvements can therefore be converted into either:

- Faster responses.
- Better-quality results.
- Lower resource consumption.

## 8. The kernel upgrade that motivated Meta's approach

Meta encountered a performance regression when moving its fleet from Linux 6.4 to 6.9, following the transition from CFS to EEVDF.

Some servers had to remain on the older kernel because the regression negatively affected ranking capacity.

```text
                Fleet
                  |
       +----------+-----------+
       |                      |
       v                      v
+-------------+        +-------------+
| Linux 6.4   |        | Linux 6.9   |
| CFS         |        | EEVDF       |
+-------------+        +-------------+
       |                      |
       v                      v
  Acceptable             Performance
  performance            regression
       |                      |
       v                      v
   Remain on              Migration
 older kernel              blocked
```

This creates an operational problem beyond the immediate performance regression.

Maintaining multiple kernel versions increases testing complexity, deployment fragmentation, maintenance costs and technical debt.

Traditionally, the available approaches would include tuning the existing scheduler, maintaining custom kernel patches or postponing the upgrade.

Maintaining custom kernel patches is particularly expensive because scheduling policy becomes coupled to kernel development.

```text
Scheduling optimization
           |
           v
 Modify kernel source
           |
           v
     Build kernel
           |
           v
    Validate kernel
           |
           v
     Deploy kernel
           |
           v
Reboot or replace hosts
```

A relatively small change to scheduling behavior becomes a system-wide infrastructure deployment.

The architectural solution is to decouple these two concerns.

## 9. Separation of mechanism and policy

One of the most important principles in operating system design is the **separation of mechanism from policy**.

**A mechanism provides a capability. A policy determines how that capability should be used.**

| Mechanism         | Policy                               |
| ----------------- | ------------------------------------ |
| Context switching | Which thread executes next           |
| CPU migration     | Where a thread should execute        |
| Preemption        | When execution should be interrupted |
| Run queues        | How runnable work should be ordered  |
| CPU wake-up       | Which idle CPU should become active  |

Traditional kernel schedulers implement both the underlying scheduling mechanisms and their associated policies within the kernel.

```text
+-------------------------------------+
| Linux kernel                        |
|                                     |
|    +---------------------------+    |
|    | Scheduling mechanisms     |    |
|    +---------------------------+    |
|                  +                  |
|    +---------------------------+    |
|    | Scheduling policy         |    |
|    +---------------------------+    |
|                                     |
+-------------------------------------+
```

An extensible scheduler introduces a programmable boundary.

```text
+-------------------------------------+
| Custom scheduling policy            |
+-------------------------------------+
                   |
         Scheduling interface
                   |
                   v
+-------------------------------------+
| Linux scheduling mechanisms         |
+-------------------------------------+
                   |
                   v
                 CPUs
```

The kernel remains responsible for executing tasks and managing their lifecycle. Scheduling decisions can be customized independently.

This is the architectural foundation of `sched_ext`.

## 10. What is sched_ext?

`sched_ext` is an extensible scheduling class that allows Linux CPU scheduling policies to be implemented using BPF programs.

It became part of upstream Linux in version 6.12.

The architecture involves two execution environments.

```text
User space

+---------------------------------------+
| Scheduler management process          |
|                                       |
| - Load scheduling policy              |
| - Configuration                       |
| - Monitoring                          |
| - Policy lifecycle management         |
+---------------------------------------+
                    |
                    | Load BPF program
--------------------+----------------------
Kernel space        |
                    v
+---------------------------------------+
| Linux scheduler core                  |
+---------------------------------------+
                    |
                    v
+---------------------------------------+
| sched_ext interface                   |
+---------------------------------------+
                    |
                    v
+---------------------------------------+
| Custom BPF scheduling policy          |
|                                       |
| - CPU selection                       |
| - Task prioritization                 |
| - Queue management                    |
| - Load balancing                      |
+---------------------------------------+
                    |
                    v
             Task execution
```

Although a user-space process loads and manages the policy, the BPF callbacks execute inside the kernel.

This distinction is fundamental. **An in-kernel BPF policy does not require a user-space round trip for each scheduling decision.**

### Event-driven scheduling

`sched_ext` exposes callbacks corresponding to scheduling events.

| Callback        | Purpose                           |
| --------------- | --------------------------------- |
| `select_cpu()`  | Suggest a CPU for a waking thread |
| `enqueue()`     | Organize runnable tasks           |
| `dispatch()`    | Supply tasks to a CPU             |
| `update_idle()` | Handle CPU idle-state transitions |
| `running()`     | Observe execution beginning       |
| `stopping()`    | Observe execution stopping        |

A simplified execution flow:

```text
    Thread wakes up
           |
           v
     select_cpu()
           |
           v
       enqueue()
           |
           v
+---------------------+
| Dispatch queue      |
+---------------------+
           |
           v
      dispatch()
           |
           v
+---------------------+
| CPU-local DSQ       |
+---------------------+
           |
           v
    Thread executes
```

Some paths bypass intermediate queues or callbacks.

Dispatch queues, or DSQs, provide the infrastructure through which custom schedulers organize runnable work. They can be global, CPU-local or custom queues.

The important architectural property is **programmability at the resource allocation boundary**.

## 11. Meta's approach: workload classification

Meta classifies threads according to their relevance to latency-sensitive execution and dynamically separates CPU capacity into two logical pools.

```text
       Runnable threads
               |
               v
     +------------------+
     | Classification   |
     +------------------+
               |
      +--------+--------+
      |                 |
  Critical        Less critical
      |                 |
      v                 v
+-----------+     +-----------+
| Queue A   |     | Queue B   |
+-----------+     +-----------+
      |                 |
      v                 v
 CPU pool A        CPU pool B
```

Consider an illustrative classification:

| Workload               | Latency sensitivity |
| ---------------------- | ------------------- |
| Request handling       | High                |
| Candidate retrieval    | High                |
| Response aggregation   | High                |
| Asynchronous logging   | Low                 |
| Background maintenance | Low                 |
| Deferred processing    | Low                 |

The classification is based on application semantics rather than exclusively on observed CPU consumption.

Two threads might have identical CPU utilization patterns but radically different effects on application performance.

A thread completing a request and a thread processing deferred maintenance may both require 1 ms of CPU time. Delaying the former could affect a user-facing operation, while delaying the latter might have no immediate consequence.

This is **semantic scheduling**: using knowledge about the purpose of work to inform its execution.

## 12. Resource isolation through CPU partitioning

Without workload isolation, latency-sensitive and background threads compete for the same CPU resources.

```text
Shared scheduling domain

Critical threads ------+
                       |
Background threads ----+----> [C0][C1][C2][C3]
                       |
Maintenance threads ---+
```

This creates interference.

A latency-sensitive thread may become runnable while CPUs are occupied by background work.

CPU partitioning establishes separate execution domains.

```text
Critical threads
            |
            v
+-----------------------+
| CPU 0 | CPU 1 | CPU 2 |
+-----------------------+

Background threads
            |
            v
+-----------------------+
| CPU 3 | CPU 4 | CPU 5 |
+-----------------------+
```

This resembles several established systems engineering patterns:

- Bulkheading.
- Dedicated thread pools.
- Workload isolation.
- Resource reservations.
- Quality-of-service differentiation.

The difference is that isolation is implemented at the CPU scheduling layer rather than exclusively at the application layer.

**A dedicated application thread pool does not automatically guarantee dedicated CPU capacity.** Its threads may still compete with unrelated thread pools once they reach the kernel.

```text
Application isolation

+-------------+   +-------------+
| Executor A  |   | Executor B  |
+-------------+   +-------------+
       |                 |
       +--------+--------+
                |
                v
       Shared kernel CPUs
```

Kernel-level scheduling can complement application-level isolation.

## 13. Hard partitioning versus soft partitioning

The simplest form of CPU partitioning is static allocation.

```text
Hard partitioning

Critical workload     Background workload
+----------------+    +----------------+
| CPU 0          |    | CPU 4          |
| CPU 1          |    | CPU 5          |
| CPU 2          |    | CPU 6          |
| CPU 3          |    | CPU 7          |
+----------------+    +----------------+

             Fixed boundary
```

The problem is that demand changes over time.

```text
Critical workload     Background workload
+----------------+    +----------------+
| CPU 0 : BUSY   |    | CPU 4 : BUSY   |
| CPU 1 : BUSY   |    | CPU 5 : IDLE   |
| CPU 2 : BUSY   |    | CPU 6 : IDLE   |
| CPU 3 : BUSY   |    | CPU 7 : IDLE   |
+----------------+    +----------------+

12 waiting tasks      0 waiting tasks
```

The machine has available CPU capacity, but the overloaded partition cannot use it.

This is known as **capacity fragmentation**.

Meta uses soft partitioning with dynamically adjusted pool sizes.

```text
Normal demand:

Critical            Background
[C0][C1][C2][C3]    [C4][C5][C6][C7]

Critical demand increases:

Critical                    Background
[C0][C1][C2][C3][C4][C5]    [C6][C7]

Critical demand decreases:

Critical        Background
[C0][C1][C2]    [C3][C4][C5][C6][C7]
```

This balances two fundamentally competing objectives.

**Resource isolation** reduces interference between workloads.

**Resource pooling** allows spare capacity to absorb fluctuations in demand.

| Property                 | Shared pool | Hard partitions | Soft partitions |
| ------------------------ | ----------- | --------------- | --------------- |
| Workload isolation       | Low         | High            | Adaptive        |
| Capacity flexibility     | High        | Low             | High            |
| Fragmentation risk       | Low         | High            | Lower           |
| Cache locality potential | Variable    | High            | High            |
| Scheduling complexity    | Low         | Moderate        | High            |

Soft partitioning does not necessarily provide hard CPU guarantees. It provides a mechanism for adaptive resource management.

## 14. Queueing theory behind CPU allocation

Consider a simplified model where each CPU can process 1,000 units of work per second.

The critical workload generates 3,800 units per second.

Initially, four CPUs are assigned to it.

```text
lambda = 3800
```

```text
mu = 4 * 1000 = 4000
```

The utilization is:

```text
rho = lambda / mu = 0.95
```

At 95% utilization, even small workload bursts can generate significant queueing delays.

Now suppose two CPUs are transferred from the background pool to the critical pool.

```text
mu = 6 * 1000 = 6000
```

```text
rho = 3800 / 6000 ~= 0.63
```

The critical workload now operates at approximately 63% utilization.

```text
Queueing
delay
  ^
  |                               /
  |                              /
  |                             /
  |                          __/
  |                   ______/
  |__________________/
  +---------------+---------+-----+---> Utilization
 0%              50%       80%  100%
```

Queueing delay generally increases nonlinearly as utilization approaches saturation, although the precise relationship depends on the arrival and service distributions.

Moving CPU capacity between workload classes can therefore have a disproportionately large effect on latency.

The underlying hardware has not changed. Total machine capacity has not increased.

Only the distribution of service capacity has changed.

**Effective resource allocation can be more valuable than additional resource provisioning.**

## 15. Dynamic resource allocation as a feedback-control system

Meta uses load-based heuristics for adjusting CPU pool sizes.

Conceptually, this is a feedback-control problem.

```text
+-----------------------+
| Workload demand       |
+-----------------------+
            |
            v
+-----------------------+
| Observe CPU pressure  | <-----+
+-----------------------+       |
            |                   |
            v                   |
+-----------------------+       |
| Allocation policy     |       |
+-----------------------+       |
            |                   |
            v                   |
+-----------------------+       |
| Resize CPU pools      |       |
+-----------------------+       |
            |                   |
            v                   |
+-----------------------+       |
| New workload state    |       |
+-----------------------+       |
            |                   |
            +-------------------+ Observe again
```

A hypothetical allocation policy could be expressed as:

```text
periodically:

    observe critical workload pressure
    observe background workload pressure

    if critical workload is overloaded:
        expand critical CPU pool

    else if critical workload has spare capacity:
        shrink critical CPU pool

    preserve minimum background capacity
```

Designing such a controller introduces familiar distributed systems problems.

| Problem                       | Potential mitigation          |
| ----------------------------- | ----------------------------- |
| Rapid allocation oscillations | Hysteresis                    |
| Temporary workload spikes     | Smoothed measurements         |
| Slow reaction to overload     | Adaptive thresholds           |
| Background starvation         | Minimum capacity reservations |
| Excessive task migration      | Reallocation cooldowns        |
| Inaccurate demand estimates   | Multiple pressure signals     |

The same control principles appear in cluster autoscaling, admission control, shard rebalancing and distributed workload placement.

The difference is the timescale and resource granularity.

## 16. CPU cache locality

Scheduling is not only about determining when a thread executes. It also determines where execution occurs.

Modern CPUs contain a hierarchy of caches.

```text
+----------+      +----------+
| Core 0   |      | Core 1   |
| L1 / L2  |      | L1 / L2  |
+----------+      +----------+
      |                 |
      +--------+--------+
               |
        +-------------+
        | Shared L3   |
        +-------------+
               |
        +-------------+
        | DRAM        |
        +-------------+
```

Actual cache topology varies across processor architectures.

When a thread executes, frequently accessed instructions and data may become resident in nearby caches.

If related threads repeatedly execute on CPUs within the same cache domain, they may benefit from existing cached data.

```text
Stable placement

Time 1: Thread A ---> CPU 0
Time 2: Thread B ---> CPU 1
Time 3: Thread A ---> CPU 0

         Shared cache domain
         Data may remain hot
```

Frequent migration across cache domains can reduce this locality.

```text
Unstable placement

Time 1: Thread A ---> Cache domain 0
Time 2: Thread A ---> Cache domain 1
Time 3: Thread A ---> Cache domain 2

         More potential cache misses
         More data movement
```

The important distinction is that a logical CPU is not simply an interchangeable execution slot.

Execution placement affects:

- Cache hit rates.
- Memory access latency.
- Memory bandwidth consumption.
- Cache coherence traffic.
- NUMA locality.
- Instructions completed per CPU cycle.

Keeping related work on consistent CPU pools helps preserve L3 locality.

CPU partitioning can therefore improve performance through two separate mechanisms:

```text
        Workload-aware placement
                    |
         +----------+-----------+
         |                      |
         v                      v
  Less contention        Better locality
         |                      |
         v                      v
Lower waiting time    Lower execution cost
         |                      |
         +----------+-----------+
                    |
                    v
          Improved performance
```

## 17. Load balancing versus locality

A naïve scheduling strategy might always assign work to the least-loaded CPU.

However, the least-loaded CPU is not necessarily the cheapest location for executing a particular task.

Consider two placement choices.

```text
CPU A
    Existing cached data
    Scheduling wait: 2 ms
    Execution time:  3 ms

CPU B
    Cold cache
    Scheduling wait: 0 ms
    Execution time:  8 ms
```

| Placement | Waiting | Execution | Total |
| --------- | ------- | --------- | ----- |
| CPU A     | 2 ms    | 3 ms      | 5 ms  |
| CPU B     | 0 ms    | 8 ms      | 8 ms  |

Despite being busier, CPU A provides a faster completion time.

A workload-aware scheduler should ideally minimize total completion cost rather than exclusively minimize CPU queue length.

```text
T_completion = T_queueing + T_execution + T_migration_overhead
```

This is analogous to data locality in distributed systems.

```text
Distributed execution:

Move computation toward cached data.


CPU scheduling:

Move threads toward cached data.
```

The same engineering principle operates at different levels of the computational hierarchy.

**Load balancing must account for the cost of moving work.**

## 18. Decoupling scheduling policies from kernel releases

Another important benefit of `sched_ext` is independent deployability.

Traditional kernel modification:

```text
   Policy change
         |
         v
Kernel modification
         |
         v
Kernel compilation
         |
         v
 Kernel validation
         |
         v
 Fleet deployment
         |
         v
   Host restart
```

BPF-based policy modification:

```text
       Policy change
             |
             v
  Build scheduler package
             |
             v
      Validate policy
             |
             v
 Restart scheduler manager
             |
             v
Load replacement BPF policy
```

The kernel version can remain unchanged.

This reduces the cost of experimentation and allows scheduling improvements to evolve independently from the underlying operating system.

The architectural pattern is familiar:

```text
Stable infrastructure mechanism
               |
      Extension interface
               |
               v
 Independently evolving policy
```

Similar designs include programmable network data planes, Kubernetes scheduling extensions, storage engine interfaces and database query optimizer rules.

A lower cost of experimentation changes what kinds of optimizations are economically feasible.

An optimization producing a relatively small improvement might not justify a fleet-wide kernel upgrade. The same optimization could justify a lightweight scheduling-policy deployment.

## 19. Reliability implications

A custom CPU scheduler occupies an extremely sensitive position in the system.

A poorly implemented application may become unavailable. A poorly implemented scheduler could affect nearly every application on a machine.

Potential failure modes include:

| Failure mode             | Consequence                                |
| ------------------------ | ------------------------------------------ |
| Incorrect classification | Critical requests delayed                  |
| Background starvation    | Maintenance backlog                        |
| Unstable allocation      | Continuous CPU pool resizing               |
| Excessive migration      | Cache thrashing                            |
| Scheduling overhead      | Reduced CPU efficiency                     |
| Priority inversion       | Critical work waits on lower-priority work |
| Incorrect dispatch logic | Runnable tasks fail to make progress       |

### Priority inversion

Consider a critical thread waiting for a lock held by a background thread.

```text
         Critical thread A
                 |
                 | Waiting for lock
                 v
        Background thread B
                 |
                 | Waiting for CPU
                 v
Scheduler prioritizes critical work
```

If the scheduler continuously deprioritizes Thread B, Thread A cannot proceed.

The scheduler must consider not only direct workload importance but also execution dependencies.

### Starvation

Background work is not necessarily optional work.

Deferred processing, resource reclamation and maintenance may eventually become critical if they accumulate sufficiently.

```text
 Background work arrives
            |
            v
+-----------------------+
| Growing backlog       |
+-----------------------+
            |
            v
   Resource exhaustion
            |
            v
  Critical-path impact
```

**A safe scheduling policy must preserve system-wide progress.**

Extensibility does not eliminate the need for careful resource accounting, workload testing, watchdog mechanisms and rollback procedures.

## 20. The engineering lessons

| Engineering principle      | Lesson                                                                                              |
| -------------------------- | --------------------------------------------------------------------------------------------------- |
| Semantic awareness         | Resource managers can make better decisions when they understand the purpose of work.               |
| Critical-path optimization | Accelerating important dependencies can be more valuable than accelerating arbitrary computations.  |
| Queueing theory            | Increasing effective service capacity for sensitive workloads can dramatically reduce waiting time. |
| Resource isolation         | Prevent unrelated computations from interfering with latency-sensitive execution.                   |
| Resource pooling           | Avoid rigid reservations that leave capacity stranded.                                              |
| Data locality              | Execution placement influences the actual cost of computation.                                      |
| Feedback control           | Adapt resource allocation according to changing workload demand.                                    |
| Separation of concerns     | Decouple resource-management mechanisms from resource-management policies.                          |
| Independent deployability  | Reduce the operational cost of performance experimentation.                                         |
| End-to-end optimization    | Evaluate infrastructure improvements using application-level outcomes.                              |
| System-wide progress       | Optimizing one workload must not destabilize its dependencies.                                      |

## 21. A broader architectural pattern: cross-layer optimization

Complex systems frequently consist of independently optimized layers.

```text
+-----------------------+
| Application           |
+-----------------------+
| Language runtime      |
+-----------------------+
| Operating system      |
+-----------------------+
| Hardware              |
+-----------------------+
```

Each layer possesses different information.

| Layer            | Knowledge                                                |
| ---------------- | -------------------------------------------------------- |
| Application      | Request importance, deadlines and dependencies           |
| Runtime          | Executors, threads, allocation and garbage collection    |
| Operating system | Runnable tasks, CPU pressure and resource availability   |
| Hardware         | Cache topology, execution resources and memory hierarchy |

A layer can make locally reasonable decisions that produce globally inefficient behavior.

Cross-layer optimization attempts to preserve abstraction boundaries while exposing enough information to improve system-wide decisions.

```text
   Application semantics
             |
             | Workload hints
             v
 Runtime execution policy
             |
             | Scheduling information
             v
Kernel resource allocation
             |
             | Hardware-aware placement
             v
    Hardware execution
```

Meta identifies finer-grained, request-specific scheduling hints as a possible future direction. This would allow scheduling decisions to reflect the changing importance of work performed by a thread, rather than relying exclusively on its predefined role.

The ultimate objective is to align resource allocation with application intent.

## Core takeaway

The most important idea is not simply that Linux supports programmable CPU schedulers.

It is that **the effectiveness of a resource allocation policy depends on the information available to it.**

A general-purpose scheduler sees competing runnable threads. A workload-aware scheduler can distinguish between computations that advance critical requests and computations that can safely wait.

By combining semantic awareness, adaptive resource isolation, cache locality and independent policy deployment, a system can extract more useful work from the same underlying hardware.

The broader systems engineering principle is:

**Performance is not merely a function of how fast computation executes. It is also a function of what executes, when it executes, where it executes, and what other computation it competes with.**
