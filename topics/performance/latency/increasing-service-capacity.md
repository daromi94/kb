# Increasing service capacity

**Service capacity increases when each request takes less processing time or when the system can process more requests concurrently.**

In queueing theory, service capacity depends primarily on two variables:

- **Service time (`S`).** How long it takes a server to process one request.
- **Number of servers (`c`).** How many independent processing units are available.

For a single server, the service rate `mu` is the reciprocal of the mean service time `E[S]`.

```text
mu = 1 / E[S]
```

For `c` identical servers, each with service rate `mu`, the theoretical aggregate service capacity is:

```text
C = c * mu = c / E[S]
```

**Aggregate capacity assumes that servers can process work independently without a shared bottleneck.**

## 1. Reduce service time

Suppose a worker processes requests in 20 milliseconds.

```text
mu = 1 / 0.020 = 50 requests/s
```

Reducing the service time to 10 milliseconds doubles its capacity:

```text
mu = 1 / 0.010 = 100 requests/s
```

```text
Before optimization:

Queue              Worker
[R][R][R] -------> [ 20 ms ]
                       |
                       v
                    50 req/s

After optimization:

Queue              Worker
[R][R][R] -------> [ 10 ms ]
                       |
                       v
                   100 req/s
```

Service time can be reduced by:

- Improving algorithms and data structures.
- Eliminating unnecessary computation.
- Reducing database queries and network round trips.
- Using caches to avoid repeated expensive operations.
- Batching operations to amortize fixed costs.
- Reducing lock contention and synchronization overhead.
- Improving CPU cache locality and memory access patterns.

**Service time** measures how long the worker takes to process the request. Reducing **queue waiting time** lets processing begin sooner.

## 2. Increase the number of servers

Instead of making one worker faster, increase the number of workers.

Suppose each worker processes 50 requests/s.

```text
                      +----------+
                  +-->| Worker 1 |--> 50 req/s
                  |   +----------+
                  |
+-------------+   |   +----------+
|    Queue    |---+-->| Worker 2 |--> 50 req/s
+-------------+   |   +----------+
                  |
                  |   +----------+
                  +-->| Worker 3 |--> 50 req/s
                      +----------+

Total = 150 req/s
```

The aggregate service capacity becomes:

```text
C = 3 * 50 = 150 requests/s
```

Independent workers can process requests in **parallel**. Adding separate processing instances is **horizontal scaling**.

However, adding workers only helps if they can make independent progress.

For CPU-bound workloads, adding more runnable threads than available CPU capacity often increases contention and context switching instead of throughput.

For I/O-bound workloads, additional concurrency may increase throughput because some requests can progress while others wait.

## 3. Increase concurrency by overlapping I/O

Overlapping I/O can increase capacity when a service spends most of its time waiting for databases, storage, or remote APIs.

Consider a request requiring:

- 2 ms of CPU processing.
- 18 ms waiting for external I/O.

Total elapsed processing time is 20 ms.

With one synchronous worker handling requests sequentially:

```text
C = 1 / 0.020 = 50 requests/s
```

But CPU demand per request is only 2 ms.

```text
Each timeline cell represents 2 ms. C = CPU, . = I/O wait.

Synchronous processing:

           Time ----->
Request A: C.........
Request B:           C.........
Request C:                     C.........

Concurrent processing:

           Time ----->
Request A: C.........
Request B:  C.........
Request C:   C.........
```

By overlapping I/O, a single CPU core could theoretically sustain up to:

```text
C_CPU = 1 / 0.002 = 500 requests/s
```

assuming sufficient I/O concurrency and no other bottlenecks.

**Overlapping I/O can improve resource utilization even when individual requests take just as long.**

For I/O-bound services, this can substantially increase effective service capacity without increasing CPU resources.

## 4. Find the bottleneck before adding capacity

**A system's throughput is limited by its most constrained resource.**

Consider a request pipeline:

```text
Incoming requests
        |
        v
+---------------+
| API workers   |   500 req/s
+---------------+
        |
        v
+---------------+
| Database      |   200 req/s
+---------------+
        |
        v
+---------------+
| Storage       |   400 req/s
+---------------+
```

If each request passes through every stage once, the stage with the lowest capacity sets the throughput limit.

```text
C_system = min(500, 200, 400) = 200 requests/s
```

Doubling API worker capacity to 1,000 requests/s does not improve system throughput.

The database remains the bottleneck.

Worse, increasing upstream concurrency may overload the database, increase its latency, and reduce effective system capacity.

**End-to-end service capacity depends on the bottleneck across the full request path.**

## 5. Connecting capacity improvements to backlog recovery

Suppose:

```text
lambda = 120 req/s
```

And current service capacity is:

```text
C = 100 req/s
```

The backlog grows at:

```text
120 - 100 = 20 req/s
```

Shorter service times and more independent workers both increase service capacity.

| Approach                   | New capacity | Backlog growth |
| -------------------------- | ------------ | -------------- |
| No improvement             | 100 req/s    | +20 req/s      |
| Reduce service time by 20% | 125 req/s    | -5 req/s       |
| Double independent workers | 200 req/s    | -80 req/s      |

A 20% reduction in service time increases the service rate by 25%.

```text
1 / (0.8 * S) = 1.25 * (1 / S)
```

**Once capacity exceeds arrivals, the queue begins draining.**

The time to drain a backlog depends on the capacity left after serving new arrivals. Assume 1,000 requests are queued, arrivals stay at 120 req/s, and service capacity stays constant throughout recovery.

```text
Drain time = Backlog / (Service capacity - Arrival rate)
```

| Service capacity | Spare capacity | Drain time   |
| ---------------- | -------------- | ------------ |
| 125 req/s        | 5 req/s        | 200 s        |
| 150 req/s        | 30 req/s       | About 33.3 s |
| 200 req/s        | 80 req/s       | 12.5 s       |

Increasing service capacity has two benefits:

1. **Higher sustainable arrival rate.** The system can process more incoming requests.
2. **Faster backlog recovery.** More spare capacity is available to process queued work.

## 6. Shared resource limits

Adding workers indefinitely does not produce indefinitely increasing throughput.

Eventually, shared resources become bottlenecks:

```text
   Workers added
         |
         v
  More concurrency
         |
         v
  Shared resource
 becomes saturated
         |
         v
  More contention
         |
         v
 Longer processing
 and waiting times
         |
         v
Throughput plateaus
 or even decreases
```

Typical causes include locks, CPU saturation, memory bandwidth, database connection limits, storage IOPS, and network bandwidth.

- **Service demand**: The actual resource time required per request, such as CPU milliseconds.
- **Response time**: The total elapsed time, including processing, queueing, contention, and waiting.
- **Service capacity**: The maximum sustainable completion rate under specified workload and resource conditions.

Optimizing service demand increases potential capacity. Adding concurrency helps exploit available resources. Neither guarantees an end-to-end throughput improvement unless the relevant bottleneck is addressed.

## 7. Capacity optimization order

With independent workers and adequate shared resources, capacity scales with the number of workers that can run in parallel and their individual service rates.

```text
Capacity = Parallelism * Per-worker service rate
```

1. **Measure the bottleneck.** Determine whether processing is CPU-bound, I/O-bound, lock-bound, or limited by a downstream service.
2. **Reduce resource demand per request.** Eliminate unnecessary work and improve processing efficiency.
3. **Increase useful concurrency.** Overlap waiting operations without overwhelming downstream components.
4. **Add resources or replicas.** Scale the actual bottleneck rather than an unrelated component.
5. **Protect the new capacity.** Use admission control and bounded queues so unexpected load cannot exhaust the system.

**Increasing the number of workers is not the same as increasing the amount of useful work a system can complete per second.**

Effective service capacity increases only when the system can complete more work without creating an equal or greater bottleneck elsewhere.
