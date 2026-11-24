# Reducing queueing time

Queueing time is the amount of time a request spends waiting before it can begin processing.

In queueing theory, this is called **waiting time in queue**, denoted by `W_q`.

Reducing queueing time is fundamentally about controlling the relationship between incoming work, processing capacity, variability, and scheduling.

The central principle is:

**Queueing delays decrease when work can begin processing sooner, not necessarily when individual requests finish processing faster.**

## 1. Understanding where queueing time comes from

Consider a service receiving requests at 90 requests per second, with a maximum processing capacity of 100 requests per second.

```text
Arrival rate: 90 req/s
            |
            v
+-----------------------+
|         QUEUE         |
|    [R][R][R][R][R]    |
+-----------------------+
            |
            v
+-----------------------+
|        WORKER         |
| Service: 10 ms/req    |
| Capacity: 100 req/s   |
+-----------------------+
            |
            v
        Completed
```

Every request experiences two distinct components of latency:

```text
R = W_q + S
```

Where:

- `R`: Response time, also called **sojourn time**.
- `W_q`: Queueing time.
- `S`: Service time.

Suppose a request waits 80 ms before receiving 10 ms of processing.

Its response time is:

```text
R = 80 + 10 = 90 ms
```

Only 10 ms is spent doing useful processing. The remaining 80 ms is spent waiting for capacity to become available.

Therefore, optimizing the actual processing time is only one way to reduce total latency.

## 2. The first lever: reduce utilization

The most important determinant of queueing delay is often **utilization**.

For a single server:

```text
rho = lambda / mu
```

Where:

- `lambda`: Arrival rate.
- `mu`: Service capacity.
- `rho`: Traffic intensity or utilization.

Consider a server capable of processing 100 requests/s.

Under an M/M/1 queueing model, average queueing time is:

```text
W_q = rho / (mu - lambda)
```

| Arrival rate | Utilization | Average queueing time |
| ------------ | ----------- | --------------------- |
| 50 req/s     | 50%         | 10 ms                 |
| 70 req/s     | 70%         | 23.3 ms               |
| 80 req/s     | 80%         | 40 ms                 |
| 90 req/s     | 90%         | 90 ms                 |
| 95 req/s     | 95%         | 190 ms                |
| 99 req/s     | 99%         | 990 ms                |

Notice what happens near full utilization.

Increasing traffic from 90 to 99 requests/s increases utilization by just 9 percentage points, but average queueing time grows from 90 ms to 990 ms.

**The relationship is nonlinear.**

### Why?

When the server is lightly utilized, it frequently becomes idle. Incoming requests can immediately begin processing.

When utilization approaches 100%, idle periods become rare. Even a small burst creates a backlog that takes longer to clear.

```text
Time runs left to right. R = arrival, [R] = request in service.
- = no arrival or idle, . = service continues beyond the six requests shown.

Low utilization:
Arrivals: --R------R-----------R----
Server:   --[R]----[R]---------[R]--
               ^      ^
               Usually available

High utilization:
Arrivals: --R-R-RR-R-RRR-RR-RR------
Server:   --[R][R][R][R][R][R]......
                ^
                Backlog forms
```

This motivates the first optimization:

**Maintain spare capacity to absorb fluctuations in demand.**

A system operating at 70% utilization may deliver substantially lower latency than the same system operating at 95%.

There is no universal optimal utilization target. It depends on arrival variability, service-time variability, latency objectives, and workload characteristics.

## 3. The second lever: reduce variability

A less obvious cause of queueing is **variability**.

Even if the average arrival rate is lower than service capacity, bursts can produce queues.

Consider two workloads:

```text
Each R marks one arrival.

Workload A: Regular arrivals
Time ----------------------------------->
R----R----R----R----R----R----R----R

Workload B: Bursty arrivals
Time ----------------------------------->
RRRRR-----------------RRRRR---------
```

Both might receive the same number of requests over a sufficiently long interval.

However, workload B creates much larger temporary backlogs.

This occurs because queueing is influenced by both:

1. **Arrival variability**: How irregularly requests arrive.
2. **Service-time variability**: How unpredictable processing durations are.

A useful approximation is Kingman's formula for a stable, single-server GI/G/1 queue:

```text
W_q ~= (rho / (1 - rho)) * ((c_a^2 + c_s^2) / 2) * E[S]
```

Where:

- `c_a`: Coefficient of variation of interarrival times.
- `c_s`: Coefficient of variation of service times.
- `E[S]`: Average service time.
- `rho`: Utilization.

This formula reveals something fundamental.

Queueing delay depends on:

```text
Utilization * Variability * Service time
```

More precisely, the utilization factor is `rho / (1 - rho)`, which diverges as utilization approaches 1.

### How to reduce variability

**On the arrival side:**

- Smooth traffic bursts using rate limiting or pacing.
- Use jitter to prevent synchronized retries.
- Avoid periodic synchronized jobs.
- Apply backpressure to regulate upstream producers.

**On the service side:**

- Eliminate unpredictable slow operations.
- Separate long-running jobs from short-running jobs.
- Reduce contention for shared resources.
- Avoid mixing radically different request types in one queue.

**Reducing variability can decrease waiting time even when average processing capacity stays unchanged.**

## 4. The third lever: reduce service time

**Making processing faster increases service capacity and often reduces queueing delay.**

For example, consider a worker with:

```text
E[S] = 10 ms
```

Its capacity is:

```text
mu = 100 req/s
```

At 90 req/s, utilization is 90%.

Now optimize service time to 8 ms.

New capacity:

```text
mu = 1 / 0.008 = 125 req/s
```

New utilization:

```text
rho = 90 / 125 = 0.72
```

Under the M/M/1 model, expected queueing time changes:

| Configuration       | Average queueing time |
| ------------------- | --------------------- |
| Before optimization | 90 ms                 |
| After optimization  | 20.6 ms               |

Reducing service time by 20% reduces expected queueing time by approximately 77% in this example.

This happens because the optimization reduces both the time required to process each request and overall utilization.

**Small improvements in service efficiency can create disproportionately large reductions in queueing delay near saturation.**

## 5. The fourth lever: improve scheduling

A queue is not only about how much work arrives. It is also about **which request gets processed next**.

This is called the **queue discipline** or **scheduling discipline**.

Consider three requests:

| Request | Service time |
| ------- | ------------ |
| A       | 100 ms       |
| B       | 10 ms        |
| C       | 10 ms        |

All arrive simultaneously, and there is one worker.

### First-Come, First-Served (FCFS)

```text
Timeline (milliseconds, 4 columns per 10 ms)

0                                       100 110 120
+---------------------------------------+---+---+
|                   A                   | B | C |
+---------------------------------------+---+---+

Waiting times:

A =   0 ms
B = 100 ms
C = 110 ms

Average = 70 ms
```

### Shortest Processing Time First (SPT)

```text
Timeline (milliseconds, 4 columns per 10 ms)

0   10  20                                      120
+---+---+---------------------------------------+
| B | C |                   A                   |
+---+---+---------------------------------------+

Waiting times:

B =   0 ms
C =  10 ms
A =  20 ms

Average = 10 ms
```

The same amount of work is processed with identical hardware and total processing capacity.

**Yet average waiting time falls from 70 ms to 10 ms.**

This demonstrates that scheduling policy can substantially affect latency.

Common disciplines include:

| Discipline              | Main objective                                      |
| ----------------------- | --------------------------------------------------- |
| FCFS / FIFO             | Preserve arrival order                              |
| Shortest Job First      | Minimize mean waiting time when job sizes are known |
| Priority Queueing       | Favor important or latency-sensitive work           |
| Round Robin             | Share processing opportunities                      |
| Processor Sharing       | Provide concurrent progress to competing jobs       |
| Earliest Deadline First | Prioritize jobs with urgent deadlines               |

There are tradeoffs.

Shortest-job-first scheduling can starve long requests if short work continuously arrives. Priority scheduling can cause similar starvation for lower-priority requests.

Fairness, deadlines, and predictable tail latency may matter more than minimizing the overall average.

## 6. The fifth lever: increase parallel processing capacity

Adding independent workers can reduce the waiting time before requests begin processing.

```text
Single worker:

+---------------+
| Queue R R R R |--------> [Worker 1]
+---------------+

Multiple workers:

                         +----------+
                    +--->| Worker 1 |
                    |    +----------+
                    |
+---------------+   |    +----------+
| Queue R R R R |---+--->| Worker 2 |
+---------------+   |    +----------+
                    |
                    |    +----------+
                    +--->| Worker 3 |
                         +----------+
```

For `c` identical workers, each with service rate `mu`:

```text
C = c * mu
```

**Adding workers decreases queueing delay when it creates additional effective processing capacity.**

However, a critical distinction exists:

**Increasing concurrency is not necessarily increasing capacity.**

For example, 16 CPU-bound workers competing for 4 CPU cores might not achieve more throughput than 4 workers.

Similarly, adding 20 database query workers can make latency worse if the underlying database is already saturated.

**The correct strategy is to add parallelism at the actual bottleneck, while preserving enough capacity in dependent resources.**

### Worker pooling

Pooling can also reduce queueing delays without adding capacity.

```text
Separate queues:

[Queue A] ---> [Worker A]  (busy)
[Queue B] ---> [Worker B]  (idle)
[Queue C] ---> [Worker C]  (idle)

Shared queue:

                +--> [Worker A]
                |
[Shared Queue] -+--> [Worker B]
                |
                +--> [Worker C]
```

With separate queues, requests may wait behind a busy worker even while other workers are idle.

A shared queue lets an available worker take the next request.

This is an example of **resource pooling**, which often improves utilization balance and reduces waiting time.

The benefit depends on the workload; locality, isolation, and contention can sometimes favor separate queues.

## 7. The sixth lever: admission control and backpressure

Sometimes the arrival rate cannot be supported, even after optimization.

Suppose:

```text
lambda = 150 req/s
```

```text
mu = 100 req/s
```

The backlog grows at 50 requests/s.

In such a situation, queueing time cannot remain bounded indefinitely if every request must be accepted and service capacity stays fixed.

There are two primary control mechanisms.

### Admission control

**Prevent excess work from entering the overloaded system.**

```text
        150 req/s
            |
            v
+-----------------------+
| Admission Controller  |
+-----------------------+
            |
            +----> Reject 50 req/s
            |
            v
        100 req/s
            |
            v
         [Queue]
            |
            v
        [Workers]
```

This protects accepted requests from a continuously growing queue.

### Backpressure

**Signal to upstream producers that processing must slow down.**

```text
[Producer] ------ Requests ------> [Consumer]
    ^                                  | Capacity pressure
    |                                  |
    +---------- Backpressure ----------+

Producer slows
```

Backpressure can prevent work from accumulating inside the consumer.

However, it does not eliminate excess demand. It moves the waiting or rate adjustment upstream. If producers cannot slow down indefinitely, admission control, load shedding, or durable buffering may still be necessary.

**A bounded queue prevents unchecked local memory growth, but its overflow behavior must be explicitly defined.**

## 8. The connection with Little's Law

Little's Law provides another perspective:

```text
L_q = lambda * W_q
```

For a stable queue:

- `L_q`: Average number of requests waiting.
- `lambda`: Effective long-run arrival/completion rate.
- `W_q`: Average queueing time.

Rearranging:

```text
W_q = L_q / lambda
```

Suppose a system completes 200 requests/s and maintains an average queue length of 1,000 requests.

```text
W_q = 1000 / 200 = 5 seconds
```

If average queue length falls to 200 requests while effective throughput remains 200 requests/s:

```text
W_q = 200 / 200 = 1 second
```

This highlights why monitoring queue length is important.

But note that Little's Law describes a relationship, not a direct optimization technique. Simply deleting queued requests reduces waiting for the surviving requests but does not increase service capacity.

## 9. Putting the strategies together

| Technique                  | What changes                | Primary effect                      |
| -------------------------- | --------------------------- | ----------------------------------- |
| Reduce utilization         | More spare capacity         | Less queue formation                |
| Reduce arrival variability | Smoother incoming traffic   | Smaller bursts                      |
| Reduce service variability | More predictable processing | Fewer long waits                    |
| Optimize processing        | Lower service time          | Higher service rate                 |
| Add workers                | More processing capacity    | Greater parallel service            |
| Improve scheduling         | Processing order            | Better latency distribution         |
| Pool workers               | Capacity allocation         | Less idle capacity while work waits |
| Admission control          | Accepted arrival rate       | Bounded overload                    |
| Backpressure               | Producer arrival behavior   | Reduced downstream accumulation     |

## 10. The central engineering lesson

**Queueing time is the result of contention for limited processing capacity.**

Four factors are especially important:

```text
W_q = f(Load, Capacity, Variability, Scheduling)
```

An effective performance-engineering approach is therefore:

1. **Determine whether the queue is stable or growing.**
2. **Measure utilization and identify the actual bottleneck.**
3. **Reduce unnecessary processing and service-time variability.**
4. **Maintain enough spare capacity to absorb bursts.**
5. **Select a scheduling discipline appropriate for latency and fairness goals.**
6. **Bound accepted work when capacity cannot keep up.**

The most important insight is that **reducing service time, reducing variability, and maintaining spare capacity can improve queueing latency far more than their individual percentages suggest.**

**Near saturation, queueing is highly nonlinear.** Preventing a system from operating continuously at its capacity limit is often more effective than trying to optimize requests after the queue has already formed.
