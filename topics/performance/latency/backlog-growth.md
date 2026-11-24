# Backlog growth

A queue grows when work arrives faster than the system can process it.

This simple observation is one of the most important principles in performance engineering, distributed systems, networking, and overload management.

The central relationship is:

```text
dQ(t)/dt = lambda(t) - mu(t)
```

Where:

- `Q(t)`: Queue length, or **backlog**.
- `lambda(t)`: **Arrival rate** — work entering the system per unit of time.
- `mu(t)`: **Service rate** — the system's processing capacity per unit of time, when fully utilized.

Strictly, this equation uses the _actual departure rate_ rather than the maximum service capacity. The distinction becomes important when the queue is empty.

## 1. Anatomy of a queue

Consider a server processing incoming requests.

```text
     Arrival rate
  lambda = 100 req/s
           |
           v
+---------------------+
| WAITING QUEUE       |
|                     |
| [R][R][R][R][R]     |
+---------------------+
           |
           v
+---------------------+
| SERVER              |
|                     |
| Service rate        |
| mu = 80 req/s       |
+---------------------+
           |
           v
      Departures
       80 req/s
```

The server can process 80 requests per second, but 100 requests arrive every second.

Therefore:

```text
Backlog growth rate = 100 - 80 = 20 requests/s
```

The backlog grows by approximately 20 requests every second while both rates remain constant and the server stays busy.

After 10 seconds:

```text
Q(10) = Q(0) + 20 * 10
```

Assuming an initially empty queue:

```text
Q(10) = 200
```

After one minute:

```text
Q(60) = 1200
```

A system can continue processing requests successfully while simultaneously accumulating an increasingly dangerous backlog.

**Processing work does not imply keeping up with incoming work.**

## 2. The fundamental queue conservation equation

The most general relationship is a conservation law:

```text
Q(t) = Q(0) + A(t) - D(t)
```

Where:

- `A(t)`: Cumulative arrivals between time 0 and `t`.
- `D(t)`: Cumulative departures during the same period.
- `Q(0)`: Initial amount of work in the system.

This is called the **queue balance equation**, or **flow conservation equation**.

Nothing disappears from the system: every unit of work must either remain in the system or leave through a departure. Departures may represent successful completion, rejection, cancellation, or dropping, depending on what the model counts.

For a queue with no drops or cancellations:

```text
 Arrivals                 Departures
    |                         ^
    v                         |
+---+-------------------------+---+
|                                 |
| Work in the system              |
|                                 |
| Q(t) = Q(0) + A(t) - D(t)       |
|                                 |
+---------------------------------+
```

For a continuously approximated workload:

```text
dQ(t)/dt = lambda(t) - d(t)
```

Here, `d(t)` is the actual **departure rate** or **throughput**, which may be smaller than the system's service capacity `mu(t)`.

For a work-conserving, single-server system:

- If the queue is nonempty, the server operates at its available capacity.
- If the queue is empty, departures cannot exceed available work.

Consequently, when the server is saturated:

```text
d(t) = mu(t)
```

And therefore:

```text
dQ(t)/dt = lambda(t) - mu(t)
```

This produces three possible regimes.

## 3. The three regimes of queue behavior

**Underloaded:** `lambda < mu`

The system has more processing capacity than incoming work requires. An existing backlog can shrink.

Example: 70 requests/s arriving, 100 requests/s capacity.

**Critically loaded:** `lambda = mu`

Arrivals exactly match processing capacity on average. There is no spare capacity to clear a backlog, and random fluctuations can still produce growing waiting times.

**Overloaded:** `lambda > mu`

Work arrives faster than it can be processed. The backlog grows continuously under sustained overload.

A fundamental measure is the **traffic intensity**, commonly interpreted as utilization:

```text
rho = lambda / mu
```

For a single server with mean service time `E[S]`, this is equivalently `rho = lambda * E[S]`.

| Traffic intensity | Interpretation                |
| ----------------- | ----------------------------- |
| `rho < 1`         | Capacity exceeds average load |
| `rho = 1`         | Critical loading              |
| `rho > 1`         | Sustained overload            |

For standard stochastic queues with unlimited waiting capacity, `rho < 1` is a necessary condition for stability and, under common assumptions, sufficient.

However, **a stable queue can still experience severe latency**.

## 4. Queueing delay increases before the system becomes overloaded

This is the most important subtlety.

Suppose an individual server takes 10 milliseconds to process a request.

Its service rate is:

```text
mu = 1 / 0.010 = 100 requests/s
```

Consider increasing the arrival rate toward this capacity.

Under the classical **M/M/1 queue** model (Poisson arrivals, exponential service times, one server, FCFS processing, unlimited buffer), the expected time spent waiting in the queue is:

```text
W_q = rho / (mu - lambda)
```

And total response time, including service, is:

```text
W = 1 / (mu - lambda)
```

```text
M/M/1 expected response time (service capacity = 100 req/s)

50%   # 20 ms
80%   ##+ 50 ms
90%   ##### 100 ms
95%   ########## 200 ms
99%   ################################################## 1,000 ms

# = 20 ms, + = 10 ms
```

Even though arrival rate remains below service capacity, latency grows dramatically as utilization approaches 100%.

| Utilization | Arrival rate | Average response time |
| ----------- | ------------ | --------------------- |
| 50%         | 50 req/s     | 20 ms                 |
| 80%         | 80 req/s     | 50 ms                 |
| 90%         | 90 req/s     | 100 ms                |
| 95%         | 95 req/s     | 200 ms                |
| 99%         | 99 req/s     | 1,000 ms              |

The reason is straightforward: a busy server has progressively less idle capacity available to absorb bursts.

This is called the **queueing effect of high utilization**.

In stochastic queueing systems, operating below maximum capacity is not merely a performance optimization; spare capacity provides resilience against variability.

## 5. Backlog growth versus backlog recovery

Consider a system with capacity of 100 requests/s.

A temporary traffic burst increases arrival rate to 150 requests/s for 20 seconds.

During the burst:

```text
Delta Q = (150 - 100) * 20 = 1000
```

The queue accumulates 1,000 requests.

After the burst, arrival rate falls to 80 requests/s.

Now:

```text
dQ/dt = 80 - 100 = -20 requests/s
```

The server can process 20 requests/s more than it receives.

Therefore, the **backlog drain time** is:

```text
T_drain = Q / (mu - lambda)
```

```text
T_drain = 1000 / (100 - 80) = 50 seconds
```

The burst lasts only 20 seconds, but its backlog requires another 50 seconds to clear.

This produces a general engineering principle:

**Recovery time depends on spare capacity, not just total processing capacity.**

## 6. Queue length and waiting time: Little's Law

Backlog is not merely a memory or storage concern. It translates into latency.

**Little's Law** states:

```text
L = lambda * W
```

Where:

- `L`: Average number of requests in the system.
- `lambda`: Long-run effective throughput.
- `W`: Average time each request spends in the system.

For the waiting queue alone:

```text
L_q = lambda * W_q
```

For example, consider a stable system handling 100 requests/s with an average of 500 requests waiting.

Then:

```text
W_q = 500 / 100 = 5 seconds
```

Five seconds of average queueing delay is implied by that backlog.

For a temporarily overloaded FIFO system, a rough estimate for a newly arriving request is:

```text
W_q(t) ~= Q(t) / mu
```

This assumes constant service capacity, no overtaking, and work units with similar processing demands. It is different from Little's Law, which describes long-run averages in a stable system.

## 7. Backlog growth in distributed systems

Queues are often hidden.

An application may have no explicit queue data structure, yet still accumulate work in:

- Network socket receive buffers.
- Thread-pool executor queues.
- Database connection-pool waiters.
- Message broker partitions.
- RPC requests awaiting responses.
- Scheduler pending-task lists.

Consider a service experiencing overload:

```text
    200 requests/s
           |
           v
+---------------------+
| Incoming queue      |
|                     |
| Q = growing         |
+---------------------+
           |
           v
+---------------------+
| Worker pool         |
|                     |
| 100 requests/s      |
+---------------------+
           |
           v
       Database
```

Without any traffic control, the backlog grows by approximately 100 requests/s.

Eventually, the accumulated work can cause:

1. Increased queueing latency.
2. Request timeouts.
3. Client retries, which may further increase the effective arrival rate.
4. Memory pressure and garbage collection overhead.
5. Worker starvation or resource exhaustion.
6. Cascading failures in downstream services.

A critical dynamic is that **overload can reduce processing capacity**.

For example:

```text
      Higher arrival rate
               |
               v
        Growing backlog <---------------------+
               |                              |
               v                              |
     Higher memory pressure                   |
               |                              |
               v                              |
More GC / contention / timeouts               |
               |                              |
               v                              |
  Lower effective service rate                |
               |                              |
               v                              |
   Even faster backlog growth                 |
               |                              |
               +-- Feedback loop -------------+
```

This is a **positive feedback loop**, often associated with overload collapse.

It explains why simply adding a larger queue rarely solves a sustained capacity problem.

## 8. Engineering approaches to controlling backlog

There are three fundamental levers:

| Strategy                     | Mechanism                                           | Tradeoff                                       |
| ---------------------------- | --------------------------------------------------- | ---------------------------------------------- |
| Increase service capacity    | More workers, replicas, efficiency improvements     | Resource costs; downstream bottlenecks         |
| Reduce admitted arrival rate | Admission control, load shedding, rate limiting     | Requests may be rejected or delayed upstream   |
| Bound the queue              | Maximum queue length and explicit overflow behavior | Dropped work, rejections, or upstream blocking |

Backpressure is particularly important because it propagates capacity constraints toward upstream producers instead of allowing unbounded accumulation.

The goal is not necessarily to eliminate queues. Queues are useful for absorbing short-lived bursts and decoupling producers from consumers.

The objective is to ensure that **queue growth remains bounded and recovery is predictable**.

## 9. The central engineering insight

Two systems may both be processing 1,000 requests per second, yet have completely different operational health.

| Metric                     | System A                          | System B    |
| -------------------------- | --------------------------------- | ----------- |
| Arrival rate               | 900 req/s                         | 1,200 req/s |
| Service capacity           | 1,000 req/s                       | 1,000 req/s |
| Throughput while saturated | 900 req/s after draining          | 1,000 req/s |
| Backlog trend              | Stable or decreasing              | +200 req/s  |
| Long-term behavior         | Stable under standard assumptions | Unstable    |

System B reports higher throughput, but is accumulating work and becoming less healthy over time.

**Throughput measures how much work the system completes. Backlog growth measures whether the system is keeping up.**

The fundamental conservation law remains:

```text
Backlog change = Arrivals - Departures
```

And the operationally important companion is:

```text
Recovery time = Backlog / Spare service capacity
```
