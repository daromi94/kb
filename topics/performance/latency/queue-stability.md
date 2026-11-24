# Queue stability

**Queue stability is the property of a queueing system that prevents its backlog from growing without bound over time.**

A stable queue can accumulate work temporarily, but it has sufficient processing capacity to handle incoming demand in the long run.

An unstable queue accumulates work faster than it can process it, causing backlog and waiting times to grow indefinitely in an unlimited-buffer model.

The fundamental relationship is:

```text
Backlog change = Arrivals - Departures
```

Queue stability is concerned with what happens to that relationship **over long periods of time**.

## 1. Stable vs. unstable queues

Consider a server receiving requests.

```text
Arrival rate
   lambda
      |
      v
+-----------+
|   QUEUE   |
| [R][R][R] |
+-----------+
      |
      v
+-----------+
|  SERVER   |
| Capacity  |
|    mu     |
+-----------+
      |
      v
 Departures
```

There are three fundamental operating regimes.

### Stable queue: Arrival rate less than service capacity

```text
lambda < mu
```

Example:

- Arrival rate: 80 requests/s
- Service capacity: 100 requests/s
- Spare capacity: 20 requests/s

**The server can eventually process all incoming work, assuming normal operating conditions and sufficient capacity over time.**

```text
Backlog
   ^
   |
 8 |      /\          /\
 6 |     /  \    /\  /  \
 4 |    /    \  /  \/    \
 2 |___/      \/          \____
 0 +----------------------------> Time

        Backlog fluctuates
        but does not diverge
```

Requests can still wait. Temporary bursts still create queues.

**The important property is that the system has enough capacity to recover.**

### Unstable queue: Arrival rate greater than service capacity

```text
lambda > mu
```

Example:

- Arrival rate: 120 requests/s
- Service capacity: 100 requests/s
- Excess arrivals: 20 requests/s

**Backlog accumulates continuously if the rates remain constant.**

```text
Backlog
   ^
   |                     __/
   |                  __/
   |               __/
   |            __/
   |         __/
   |      __/
   |   __/
   |__/
 0 +----------------------------> Time

        Backlog grows
        without bound
```

After 60 seconds:

```text
Q(60) = (120 - 100) * 60 = 1200
```

After 10 minutes:

```text
Q(600) = 12,000
```

The system may continue completing 100 requests every second, but it is falling further behind.

**A system can have high throughput while being unstable.**

### Critical loading: Arrival rate equals service capacity

```text
lambda = mu
```

This is a particularly interesting regime.

**The server has exactly enough average capacity to match incoming work, but no spare capacity to recover from fluctuations.**

```text
Backlog
   ^
   |             /\
   |        /\  /  \     /\
   |   /\  /  \/    \   /  \
   |  /  \/          \_/    \
   |_/                       \...
   +----------------------------> Time

        No spare capacity
        to reliably drain bursts
```

In a standard stochastic M/M/1 queue, this is not a stable regime: there is no stationary queue-length distribution.

However, equality does not always imply instability for every queueing model. A perfectly deterministic D/D/1 system can operate at equal arrival and service rates without accumulating a growing backlog.

The important distinction is **variability**.

## 2. Traffic intensity and the stability condition

Queueing theory uses a variable called **traffic intensity**, denoted by `rho`.

For a single server:

```text
rho = lambda / mu
```

Where:

- `lambda`: Average arrival rate.
- `mu`: Service capacity.
- `rho`: Traffic intensity.

For a single-server queue, this is also the fraction of time the server must be busy to process the offered load, provided the system is stable and work-conserving.

| Traffic intensity (`rho`) | Interpretation                 |
| ------------------------- | ------------------------------ |
| 0.50                      | 50% utilization                |
| 0.80                      | 80% utilization                |
| 0.95                      | 95% utilization                |
| 1.00                      | Critical loading               |
| 1.20                      | Demand exceeds capacity by 20% |

For classical queues with a single work-conserving server, stationary arrivals, and standard independence and regularity assumptions:

```text
rho < 1
```

is the fundamental stability condition.

For `c` identical servers with individual service rate `mu`:

```text
rho = lambda / (c * mu)
```

This formula assumes workers have independent processing capacity.

Importantly, `rho < 1` is a capacity condition, not a universal guarantee of stability for arbitrary scheduling policies, dependencies, or network topologies.

## 3. Why a stable queue can still have terrible latency

This is one of the most important lessons in queueing theory.

**A queue can be mathematically stable while delivering unacceptable performance.**

Consider a server with capacity:

```text
mu = 100 req/s
```

Compare three workloads.

| Arrival rate | Utilization | Stable? |
| ------------ | ----------- | ------- |
| 50 req/s     | 50%         | Yes     |
| 90 req/s     | 90%         | Yes     |
| 99 req/s     | 99%         | Yes     |

All three are stable under the classical M/M/1 model.

However, they have drastically different waiting times.

For an M/M/1 queue:

```text
W_q = rho / (mu - lambda)
```

| Utilization | Average queueing delay |
| ----------- | ---------------------- |
| 50%         | 10 ms                  |
| 60%         | 15 ms                  |
| 70%         | 23.3 ms                |
| 80%         | 40 ms                  |
| 90%         | 90 ms                  |
| 95%         | 190 ms                 |
| 99%         | 990 ms                 |

M/M/1 queue with service capacity of 100 requests per second.

Notice:

- At 50% utilization: 10 ms average queueing delay.
- At 90% utilization: 90 ms.
- At 99% utilization: 990 ms.

The queue is still stable at 99% utilization, but its average waiting time is almost one second.

Why?

Because the server has almost no spare capacity to drain accumulated work.

This establishes an important distinction:

**In this model, stability means the queue length has a steady-state distribution. Performance is about how much waiting occurs within that stable regime.**

A system can satisfy the mathematical stability condition and still violate every latency objective.

## 4. Stability is a long-run property

**A queue is not necessarily unstable just because its backlog grows temporarily.**

Suppose a server has a capacity of 100 requests/s.

Incoming traffic follows this pattern:

| Period           | Arrival rate | Capacity  | Backlog change |
| ---------------- | ------------ | --------- | -------------- |
| First 10 seconds | 150 req/s    | 100 req/s | +500 requests  |
| Next 25 seconds  | 80 req/s     | 100 req/s | -500 requests  |

During the initial burst:

```text
Q(10) = 500
```

After the burst ends:

```text
Drain rate = 100 - 80 = 20 req/s
```

Time required to clear the backlog:

```text
T_drain = 500 / 20 = 25 seconds
```

```text
Backlog (requests)
    ^
500 |          *
400 |        *      *
300 |      *             *
200 |    *                    *
100 |  *                           *
  0 |*----------------------------------*-> Time
     0 s       10 s                     35 s
     |<-Burst->|<------- Recovery ------>|
```

The backlog grows during the burst, but eventually returns to zero.

This is called **transient backlog accumulation**.

The opposite is **sustained overload**, where incoming demand continues exceeding processing capacity without sufficient recovery periods.

**A stable system can experience transient overload.** Stability does not require the queue to decrease at every instant.

## 5. Formal meaning of queue stability

There are multiple mathematical definitions of stability.

One important concept is **positive recurrence**.

For a Markovian queue, positive recurrence means the queue-length process returns to its states in finite expected time and possesses a stationary probability distribution (under the standard irreducibility assumptions).

For example, in a stable M/M/1 queue:

```text
P(N = n) = (1 - rho) * rho^n
```

Where `N` is the number of requests in the system, including any request in service.

This describes the probability of observing exactly `n` requests in the system in steady state.

The expected number of requests is:

```text
E[N] = rho / (1 - rho)
```

At 90% utilization:

```text
E[N] = 0.9 / 0.1 = 9
```

At 99% utilization:

```text
E[N] = 0.99 / 0.01 = 99
```

Both queues have stationary distributions, but the second contains far more work on average.

Another useful definition is **strong stability**, which requires the long-run time-average expected backlog to remain finite:

```text
limsup_(T -> infinity) (1 / T) * sum(E[Q(t)], t = 0 to T - 1) < infinity
```

This is commonly used when analyzing scheduling and control algorithms in networks.

A weaker notion, **rate stability**, requires backlog to grow sublinearly:

```text
lim_(t -> infinity) Q(t) / t = 0
```

**Rate stability does not necessarily imply a finite average queue length.**

These distinctions matter when examining distributed scheduling algorithms and stochastic network stability.

## 6. The role of variability

Average arrival rate alone does not describe how requests reach a system.

Consider two workloads with an average of 80 requests/s and capacity of 100 requests/s.

```text
Workload A: Smooth arrivals

Time -------------------------------->

R---R---R---R---R---R---R---R---R---

Small queues, frequent idle periods.

Workload B: Bursty arrivals

Time -------------------------------->

RRRRR-----------RRRR----------------

Large queues during bursts, followed by recovery periods.
```

Both workloads have the same average rate.

Yet workload B may experience substantially longer waiting times.

Why?

Because the queue must absorb the temporary mismatch between instantaneous arrivals and service capacity.

Variability in service times has a similar effect.

A request taking 5 seconds can cause many short requests to wait behind it in a FIFO queue.

For a stable GI/G/1 queue, Kingman's approximation illustrates the effect:

```text
W_q ~= (rho / (1 - rho)) * ((c_a^2 + c_s^2) / 2) * E[S]
```

Where:

- `c_a^2`: Squared coefficient of variation of interarrival times.
- `c_s^2`: Squared coefficient of variation of service times.

The important insight is:

**A queue may be stable in terms of average demand while still suffering substantial delays because of variability.**

## 7. Stability in distributed systems

Queue stability becomes more complicated when requests flow through multiple services.

Consider:

```text
  150 req/s
      |
      v
+-----------+
| Service A |
| 200 req/s |
+-----------+
      |
      v
+-----------+
| Service B |
| 100 req/s |
+-----------+
      |
      v
+-----------+
| Service C |
| 300 req/s |
+-----------+
```

Assume every request passes through all three services.

Service A has enough capacity to process the arriving workload.

But Service B cannot process more than 100 requests/s.

Its backlog grows at:

```text
150 - 100 = 50 requests/s
```

The system is globally unstable, even though two of its three services have more than enough capacity.

This demonstrates a fundamental principle:

**End-to-end stability depends on the ability of every required bottleneck resource to handle its offered workload.**

Adding resources to Service A will not solve the problem.

**The processing capacity of Service B must increase, or the admitted arrival rate must decrease.**

### Feedback can make instability worse

Consider an overloaded service:

```text
Incoming demand <---- More incoming demand ----+
       |                                       |
       v                                       |
Growing backlog                                |
       |                                       |
       v                                       |
 Higher latency                                |
       |                                       |
       v                                       |
Request timeouts                               |
       |                                       |
       v                                       |
    Retries -----------------------------------+
```

Retries increase the effective arrival rate.

If the original demand was 100 req/s, retries may increase the actual load to 140 or 180 req/s.

The system becomes even more overloaded.

This is a **positive feedback loop** that can contribute to congestion collapse.

Queue stability analysis therefore must account for retries, feedback, and shared downstream dependencies, not just initial incoming requests.

## 8. Does bounding queue size guarantee stability?

Consider a queue with a maximum capacity of 1,000 requests.

```text
     150 req/s
         |
         v
+-----------------+
|  Bounded queue  |
| Capacity: 1000  |
+-----------------+
         |
         v
+-----------------+
|     Worker      |
|    100 req/s    |
+-----------------+

Excess requests are rejected
or dropped when the queue fills.
```

The queue length cannot grow beyond 1,000.

Does that make the system stable?

**It makes the backlog bounded, but it does not mean all incoming demand can be served.**

**Under sustained excess demand, the queue eventually fills, and requests must be dropped, rejected, or blocked upstream.**

A finite-buffer stochastic queue may have a stationary queue-length distribution even when offered demand exceeds service capacity, because overflow is discarded.

This distinction is essential:

- **Queue-length stability:** The amount of buffered work remains bounded.
- **Demand sustainability:** Incoming work can be completed at the required rate without persistent rejection or loss.
- **Latency stability:** Delays remain within acceptable operating limits.

Bounding queue size solves the memory-growth problem, but not necessarily the excess-demand problem.

## 9. How to determine whether a production queue is stable

Several measurements help establish queue health.

| Metric              | Question it answers                    |
| ------------------- | -------------------------------------- |
| Arrival rate        | How much work enters?                  |
| Departure rate      | How much work completes or exits?      |
| Service capacity    | How much could be processed?           |
| Utilization         | How close is the system to saturation? |
| Queue length        | How much work is waiting?              |
| Queueing delay      | How long is work waiting?              |
| Rejection/drop rate | Is demand being discarded?             |
| Backlog growth rate | Is the system falling behind?          |

One especially useful operational signal is:

```text
Delta Q / Delta t
```

**If backlog increases consistently across long observation windows, the system may be overloaded.**

If backlog fluctuates around a reasonably stationary range, the queue may be stable.

However, a short monitoring window cannot prove mathematical stability; and bounded queues can conceal overload through dropped requests.

### Backlog behavior

```text
STABLE

Q
|     /\      /\    /\
|  /\/  \  /\/  \  /  \
|_/      \/      \/    \__
+--------------------------> t

UNSTABLE

Q
|                     /
|                  /
|              ___/
|         ____/
|    ____/
|___/
+--------------------------> t
```

For capacity planning, the objective is not merely to satisfy `rho < 1`.

It is to operate with enough headroom that fluctuations, processing variability, and temporary failures can be absorbed without violating latency or reliability requirements.

## 10. Key engineering principles

1. **Stable does not mean empty.** A stable queue can contain substantial work.
2. **Stable does not mean fast.** Near saturation, queueing delays can become very large even when the system remains mathematically stable.
3. **Transient backlog growth does not imply instability.** Temporary bursts are acceptable when adequate recovery capacity exists.
4. **Average capacity must exceed average demand under standard stochastic queue models.** But the average-rate condition alone may not establish stability in arbitrary networks.
5. **The bottleneck determines end-to-end throughput.** Every required stage must sustain its offered workload.
6. **Bounded queues prevent unbounded accumulation, not overload.** Rejections, dropped work, or upstream blocking may still occur.
7. **Spare capacity provides recovery ability.** A system with no headroom cannot rapidly drain accumulated backlog.

The fundamental distinction is:

```text
Queue stability != Good queueing performance
```

Queue stability establishes whether a system can sustain its workload in the long run. Queueing performance establishes how effectively the system handles that workload, especially during bursts and periods of high utilization.
