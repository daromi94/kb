# Thread pool sizing

Determining the correct number of threads depends on task nature and hardware. A
pool too small leads to underutilized resources and high latency; too large
causes excessive context switching and risks `OutOfMemoryError` from thread
stack overhead.

Per Brian Goetz in *Java Concurrency in Practice*, sizing splits into two
categories: CPU-bound and I/O-bound tasks.

## CPU-bound tasks

CPU-bound tasks require intense computation with minimal interruption (matrix
multiplication, image processing, encryption). They don't wait for external
resources.

Adding more threads than physical cores doesn't improve performance—it degrades
it because the OS wastes time swapping threads on and off cores.

**Optimal formula:**

$$N_{threads} = N_{cpus} + 1$$

The "+1" acts as a spare. If a primary thread pauses (page fault, background OS
task), the spare steps in so the CPU core never sits idle.

## I/O-bound tasks

I/O-bound tasks spend most time waiting for external events (database queries,
REST calls, file reads). During wait time, the thread is blocked and the CPU
becomes available for other work.

**Universal sizing formula:**

$$N_{threads} = N_{cpus} \times U_{cpu} \times \left(1 + \frac{W}{C}\right)$$

- $N_{cpus}$ = number of cores (`Runtime.getRuntime().availableProcessors()`)
- $U_{cpu}$ = desired CPU utilization (0.0 to 1.0)
- $W/C$ = ratio of waiting time to computing time

**Example:** 4-core machine, 100% CPU utilization target, tasks spend 100ms
waiting for database and 10ms processing ($W/C = 10$):

$$4 \times 1 \times (1 + 10) = 44 \text{ threads}$$

## Memory constraints

While the formulas optimize for CPU, consider memory (RAM). Every thread has its
own stack memory, typically 1MB by default.

- **Thread stack cost:** 1,000 threads ≈ 1 GB RAM just for stacks
- **Heap pressure:** More threads mean more simultaneous object creation,
  increasing GC pause frequency
- **Rule of thumb:** If calculations suggest 1,000 threads but you only have
  2 GB RAM, lower the thread count and increase queue size instead

## Little's Law for queue sizing

To determine work queue size, use Little's Law to predict items in a stable
system:

$$L = \lambda \times W$$

- $L$ = average tasks in the system (threads + queue)
- $\lambda$ = arrival rate (tasks per second)
- $W$ = average time a task spends in the system (latency)

If your pool handles 100 requests/sec and each takes 0.5s, you need to hold
$100 \times 0.5 = 50$ tasks. With a thread pool size of 10, your queue needs to
be at least 40 to prevent rejection.

## Practical approach

Because $W/C$ ratios are hard to measure precisely:

1. **Start with a fixed pool** using the formula as a baseline
2. **Expose metrics:** Use Micrometer or JMX to monitor `getPoolSize()`,
   `getQueueSize()`, and `getActiveCount()`
3. **Adjust dynamically:** If the queue is always full but CPU usage is low,
   increase thread count. If CPU is at 100% and latency is high, you've hit the
   physical limit
