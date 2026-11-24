# Convoy effect

The **convoy effect** is a queueing phenomenon in which a long-running or slow operation delays multiple shorter operations that are waiting behind it.

It typically occurs when a scheduling discipline requires requests to be processed in arrival order, or when multiple execution units compete for an exclusive resource.

The name comes from the analogy of vehicles traveling behind a slow truck on a road where overtaking is impossible.

```text
Direction of travel ---->

[Car][Car][Car][Car][Slow Truck] ---------->
                          |
                          +-- Limits everyone's progress
```

Although the cars are individually capable of moving faster, their progress is constrained by the slowest vehicle ahead of them.

The same phenomenon occurs in software systems.

## 1. How the convoy effect occurs

Consider a single worker processing requests using First-Come, First-Served (FCFS) scheduling.

Five requests arrive simultaneously:

| Request | Service time |
| ------- | ------------ |
| A       | 500 ms       |
| B       | 10 ms        |
| C       | 10 ms        |
| D       | 10 ms        |
| E       | 10 ms        |

Request A enters the queue first.

```text
                        Execution order
                               |
                               v
+---+---+---+---+---+      +--------+
| E | D | C | B | A | ---> | Worker |
+---+---+---+---+---+      +--------+
```

The resulting execution timeline is:

```text
Time (ms, // marks a break in scale)

0                           500   510   520   530   540
+--------//-----------------+-----+-----+-----+-----+
|        //   A             |  B  |  C  |  D  |  E  |
+--------//-----------------+-----+-----+-----+-----+
```

The waiting times are:

| Request | Queueing time | Service time | Response time |
| ------- | ------------- | ------------ | ------------- |
| A       | 0 ms          | 500 ms       | 500 ms        |
| B       | 500 ms        | 10 ms        | 510 ms        |
| C       | 510 ms        | 10 ms        | 520 ms        |
| D       | 520 ms        | 10 ms        | 530 ms        |
| E       | 530 ms        | 10 ms        | 540 ms        |

Average queueing time:

```text
W_q = (0 + 500 + 510 + 520 + 530) / 5
```

```text
W_q = 412 ms
```

The shorter requests require only 10 milliseconds of actual processing, yet experience more than 500 milliseconds of response time.

**A single expensive request has effectively degraded the performance of every request behind it.**

## 2. Why the convoy effect occurs

Three conditions commonly contribute to the convoy effect:

- **Service-time variability:** Some requests take considerably longer than others.
- **Ordered or exclusive execution:** Requests cannot bypass the slow operation.
- **Resource contention:** Multiple requests depend on the same limited processing resource.

The underlying problem is that requests become **temporally coupled** through a shared resource.

```text
Request A ----+
Request B ----+
Request C ----+----> Shared resource
Request D ----+     (exclusive access)
Request E ----+
```

Even though the requests may be logically independent, their execution times become dependent on one another.

**A slow request introduces delays into otherwise unrelated requests.**

## 3. Service-time variability and residual service time

The mathematical explanation behind the convoy effect involves **residual service time**.

Residual service time is the remaining processing time of the operation currently occupying a server.

```text
Request A: 500 ms
|-------------------------------------------------|
0                   200                           500
                    ^
                    |
                    Request B arrives

                    |-----------------------------|
                    Remaining 300 ms
```

**Request B must wait at least 300 milliseconds before it can begin processing.**

An important observation from queueing theory is that randomly arriving requests are disproportionately likely to encounter long-running operations.

A request lasting 500 milliseconds occupies a server for 50 times as long as a request lasting 10 milliseconds. Consequently, it is much more likely to be encountered by an independent arrival while it is executing.

This is related to the **inspection paradox**.

### Pollaczek–Khinchine formula

For a stable M/G/1 queue with FCFS scheduling, the expected queueing time is:

```text
W_q = lambda * E[S^2] / (2 * (1 - rho))
```

Where:

- `lambda`: Arrival rate.
- `S`: Service time.
- `E[S^2]`: Second moment of service time.
- `rho`: Server utilization.

The second moment can be expressed as:

```text
E[S^2] = Var(S) + E[S]^2
```

Therefore:

```text
W_q = lambda * (Var(S) + E[S]^2) / (2 * (1 - rho))
```

This reveals a fundamental property:

**Queueing delay increases with service-time variance, even when average service time and utilization remain unchanged.**

A small number of exceptionally slow requests can disproportionately increase average waiting time.

## 4. Same capacity, different queueing performance

Consider two systems receiving Poisson arrivals at 8 requests/s.

Both have an average service time of 100 milliseconds and a service capacity of 10 requests/s.

### System A: Predictable processing

Every request takes exactly 100 milliseconds.

```text
[A:100ms][B:100ms][C:100ms][D:100ms]
```

### System B: Highly variable processing

90% of requests take 10 milliseconds.

10% of requests take 910 milliseconds.

```text
[A:10ms][B:10ms][----- C:910ms -----][D:10ms]
```

Both systems have identical mean service times and utilization.

However, applying the M/G/1 formula produces:

| Metric             | System A | System B |
| ------------------ | -------- | -------- |
| Mean service time  | 100 ms   | 100 ms   |
| Service capacity   | 10 req/s | 10 req/s |
| Utilization        | 80%      | 80%      |
| Mean queueing time | 200 ms   | 1,658 ms |
| Mean response time | 300 ms   | 1,758 ms |

System B experiences approximately **8.3 times more queueing delay** without any reduction in average service capacity.

**This is why average processing time alone is insufficient for understanding system performance.**

## 5. Convoy effect in operating systems

The convoy effect is a classical problem in CPU scheduling, particularly with non-preemptive FCFS scheduling.

Consider a mixture of CPU-bound and I/O-bound processes.

```text
Ready queue:

+------+------+------+-------------------+
| IO-3 | IO-2 | IO-1 | CPU-bound process | ---> CPU
+------+------+------+-------------------+
```

The CPU-bound process occupies the CPU for an extended period.

Meanwhile, the I/O-bound processes need only short CPU bursts before initiating I/O operations.

```text
Time ---------------------------------------------->

CPU:  [--------- CPU-bound ---------][IO1][IO2][IO3]
Disk: [---------------Idle---------------][-Active-]
```

While the CPU-bound process executes:

- I/O-bound processes wait in the ready queue.
- I/O devices may remain idle.
- Opportunities to overlap computation and I/O are lost.

Later, the I/O-bound processes initiate their operations and block, potentially leaving the CPU underutilized.

**The result is poor utilization across multiple resources.**

Preemptive scheduling disciplines such as Round Robin mitigate this problem by allowing short CPU bursts to execute without waiting for a long-running process to finish.

```text
Time ----------------------------------->

CPU:  [CPU][IO1][CPU][IO2][CPU][IO3][CPU]
Disk:           [------Active I/O-------]
```

The system achieves better overlap between CPU processing and I/O.

## 6. Lock convoying

A related phenomenon is the **lock convoy**, which occurs when multiple threads accumulate behind a contended lock.

```text
Thread A ----> [Acquired lock] <---------+
                                         |
Thread B ----> [Waiting] ----------------+
                                         |
Thread C ----> [Waiting] ----------------+
                                         |
Thread D ----> [Waiting] ----------------+
                                         |
Thread E ----> [Waiting] ----------------+
```

Suppose Thread A acquires a mutex and then performs a slow operation inside the critical section.

```text
lock(mutex);

read_from_disk();
process_data();

unlock(mutex);
```

**Every other thread requiring the mutex must wait.**

Even worse, the lock holder may be descheduled by the operating system while holding the lock.

```text
Thread A acquires lock
          |
          v
Thread A is descheduled
          |
          v
Other threads attempt acquisition
          |
          v
Threads block behind the lock
          |
          v
Thread A resumes
          |
          v
Thread A releases lock
          |
          v
Waiting threads compete for ownership
```

Under sustained contention, repeated lock handoffs, thread wakeups, and context switches can consume significant processing capacity.

Unlike a simple FIFO convoy, lock convoying can therefore reduce both latency performance and effective throughput.

Common mitigation techniques include shorter critical sections, finer-grained locking, state partitioning, and eliminating blocking I/O inside critical sections.

## 7. Convoy effect in distributed systems

### Database connection pools

Consider a connection pool containing four connections.

```text
                       +-------------------+
                  +--->| Connection 1: 5s  |
                  |    +-------------------+
                  |
                  |    +-------------------+
                  +--->| Connection 2: 8s  |
                  |    +-------------------+
[Waiting Queue] --+
                  |    +-------------------+
                  +--->| Connection 3: 10s |
                  |    +-------------------+
                  |
                  |    +-------------------+
                  +--->| Connection 4: 7s  |
                       +-------------------+
```

All connections are occupied by expensive analytical queries.

Short transactional queries requiring only a few milliseconds must wait until a connection becomes available.

**The short queries experience high latency despite requiring little processing.**

### Thread pools

A similar problem occurs when long-running background tasks and latency-sensitive requests share a thread pool.

```text
Shared thread pool

                    +-----------+
               +--->| Long task |
               |    +-----------+
               |
               |    +-----------+
[Task Queue] --+--->| Long task |
               |    +-----------+
               |
               |    +-----------+
               +--->| Long task |
                    +-----------+

Short requests remain queued.
```

The system may have sufficient CPU capacity, but insufficient available worker slots.

### Distributed query engines

A small number of expensive query tasks can occupy execution slots needed by shorter queries.

```text
Execution slots:

Slot 1: [--------- Large query ---------]
Slot 2: [--------- Large query ---------]
Slot 3: [--------- Large query ---------]
Slot 4: [--------- Large query ---------]

Waiting:

[Small query][Small query][Small query]
```

This is one reason distributed execution engines introduce workload management, resource groups, fair scheduling, admission control, and workload isolation.

## 8. Convoy effect vs. head-of-line blocking

These concepts are closely related, but emphasize different aspects of queueing behavior.

|                 | Convoy effect                                        | Head-of-line blocking                                        |
| --------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| Focus           | Delays propagated across multiple waiting jobs       | A job at the front prevents subsequent jobs from progressing |
| Typical cause   | Long service time or prolonged resource ownership    | Ordering constraints or unavailable resources                |
| Common examples | CPU scheduling, mutex contention                     | Network switches, ordered message processing                 |
| Consequences    | Increased latency and potentially reduced throughput | Prevented progress of otherwise executable work              |

**Head-of-line blocking can be a mechanism that produces the convoy effect.**

However, the convoy effect can also occur without an explicit FIFO queue, as demonstrated by lock contention.

## 9. How to mitigate the convoy effect

### Shortest Job First (SJF)

Process shorter requests before longer ones when service-time estimates are available.

```text
FIFO:

[---------- Long ----------][S][S][S][S]

SJF:

[S][S][S][S][---------- Long ----------]
```

For the original example, average queueing time decreases from 412 milliseconds to 20 milliseconds.

The total amount of work remains unchanged.

**The disadvantage** is that long-running requests may suffer starvation.

### Preemptive scheduling

Interrupt long-running operations so other operations can make progress.

```text
Without preemption:

[---------- A ----------][B][C][D]

With preemption:

[A][B][A][C][A][D][A][A][A]
```

Examples include Round Robin and Shortest Remaining Processing Time (SRPT).

Preemption introduces context-switching overhead and is not always feasible for arbitrary operations.

### Workload isolation

Separate workloads according to their processing characteristics.

```text
                    +------------+
Short requests ---->| Fast queue |----> Worker pool A
                    +------------+

                    +------------+
Long requests  ---->| Slow queue |----> Worker pool B
                    +------------+
```

This prevents expensive operations from monopolizing resources required by latency-sensitive operations.

This pattern is closely related to **bulkheading**.

**The tradeoff** is reduced resource-pooling efficiency when one workload has idle capacity while another is overloaded.

### Task decomposition

Break large operations into smaller, independently schedulable units.

```text
Before:

[------------ Large task ----------]

After:

[Chunk 1][Chunk 2][Chunk 3][Chunk 4]
```

Smaller execution units create more scheduling opportunities.

This is particularly useful in distributed query engines, cooperative schedulers, event loops, and data-processing systems.

**The tradeoff** is increased scheduling, coordination, and state-management overhead.

### Reduce service-time variability

Optimize exceptionally slow operations rather than focusing exclusively on average processing time.

**Reducing the duration of the slowest requests can have a disproportionate impact on the waiting times of other requests.**

This is especially valuable in systems with heavy-tailed service-time distributions.

## 10. Engineering implications

The convoy effect demonstrates why several commonly monitored metrics are insufficient in isolation:

| Metric               | What it can conceal                                 |
| -------------------- | --------------------------------------------------- |
| Average service time | Exceptionally expensive requests                    |
| Average utilization  | Temporary resource monopolization                   |
| Throughput           | Severe waiting times for short requests             |
| Queue length         | Differences in the processing demand of queued work |
| Worker count         | Workers occupied by slow or blocked operations      |

Useful additional measurements include service-time percentiles, service-time variance, resource holding time, queueing latency by workload class, lock contention time, and the age of waiting requests.

## 11. The fundamental engineering lesson

The convoy effect demonstrates that **performance isolation is as important as processing efficiency**.

**A slow operation should ideally make only itself slow.** In poorly isolated systems, it makes every operation sharing its resources slow.

```text
Poor isolation:

Slow request
     |
     +----> Delayed request
     +----> Delayed request
     +----> Delayed request
     +----> Delayed request

Good isolation:

Slow request ----> Slow completion

Fast request ----> Fast completion
Fast request ----> Fast completion
Fast request ----> Fast completion
```

Increasing service capacity is not the only way to improve queueing performance. Changing how work competes for capacity can produce substantial improvements without increasing hardware resources.

**Service-time variability creates the potential for convoys. Scheduling and resource-sharing policies determine how far their effects propagate.**
