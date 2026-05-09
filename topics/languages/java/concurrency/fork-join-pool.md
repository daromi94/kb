# Fork join pool

ForkJoinPool is a specialized ExecutorService designed for **recursive,
divide-and-conquer** tasks. While ThreadPoolExecutor is built for independent,
externally submitted tasks, ForkJoinPool is optimized for tasks that spawn
subtasks and wait for them to finish.

It powers parallel streams and the CompletableFuture framework.

## The fork-join pattern

1. **Fork:** A large task splits into smaller, independent subtasks
2. **Compute:** Each subtask is solved. If still too large, fork again
3. **Join:** Subtask results are combined back together for the final result

## Work-stealing algorithm

The critical difference from a normal thread pool:

**Local deques:** Every worker thread has its own private double-ended queue
(deque) of tasks.

**LIFO for the owner:** A thread pushes new subtasks onto the head of its
deque and pops from the head (Last-In, First-Out). This keeps recently
created (cache-warm) subtasks within the same thread.

**FIFO for the thief:** If a thread finishes its work, it "steals" from the
tail of another thread's deque (First-In, First-Out). Tasks at the tail are
usually oldest and largest — when stolen, they'll likely be subdivided
further, keeping the thief busy longer.

## The common pool

`ForkJoinPool.commonPool()` is a static, shared instance.

- **Automatic scaling:** Creates threads equal to `availableProcessors() - 1`
- **Shared resource:** Avoid running blocking I/O in the common pool — it
  can starve other parts of your application (like parallel streams) that
  rely on it

## ForkJoinPool vs ThreadPoolExecutor

Per Doug Lea and Brian Goetz:

- **ThreadPoolExecutor** is for **concurrency** — handling many independent
  requests (like HTTP requests in a web server), maximizing throughput by
  overlapping I/O wait times
- **ForkJoinPool** is for **parallelism** — data-parallel tasks that break
  large computational problems into smaller pieces across all CPU cores,
  minimizing total calculation time

| Feature               | ThreadPoolExecutor            | ForkJoinPool                       |
|-----------------------|-------------------------------|------------------------------------|
| **Task model**        | Independent external tasks    | Recursive subtask spawning         |
| **Work distribution** | Shared global queue           | Per-thread deques + work-stealing  |
| **Idle behavior**     | Wait on global queue          | Steal from busy threads            |
| **Blocking I/O**      | Handles blocked I/O well      | Prefers pure computation           |
| **Join support**      | Blocking to wait is expensive | Designed for efficient joins       |
| **Efficiency goal**   | Throughput of many requests   | Minimum latency for one large task |
| **Java usage**        | Tomcat, Netty, general APIs   | Parallel streams engine            |

---

Return to [Concurrency](_index.md)
