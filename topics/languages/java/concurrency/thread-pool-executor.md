# Thread pool executor

ThreadPoolExecutor is the extensible, low-level implementation of
ExecutorService. While the Executors factory provides pre-configured pools,
ThreadPoolExecutor allows fine-tuning exactly how threads are created, how
many can exist, and how they behave under heavy load.

## Internal mechanism

When a task is submitted via `execute(Runnable)`:

1. **Core pool size:** If fewer than `corePoolSize` threads are running,
   create a new thread to run the task, even if other workers are idle
2. **The queue:** If `corePoolSize` or more threads are running, place the
   task in the BlockingQueue
3. **Maximum pool size:** If the queue is full and fewer than
   `maximumPoolSize` threads are running, create a new non-core thread
4. **Rejection:** If the queue is full and `maximumPoolSize` threads are
   already running, pass the task to a RejectedExecutionHandler

## Core parameters

| Parameter           | Purpose                                                      |
|---------------------|--------------------------------------------------------------|
| **corePoolSize**    | Threads to keep in the pool, even if idle                    |
| **maximumPoolSize** | Absolute ceiling on threads allowed                          |
| **keepAliveTime**   | How long excess threads (above core) wait before terminating |
| **workQueue**       | Queue holding tasks before execution                         |

## Queue types

The behavior changes drastically based on the queue:

**Unbounded (LinkedBlockingQueue):** What `newFixedThreadPool()` uses. The
queue grows indefinitely. The pool never exceeds `corePoolSize`, and
`maximumPoolSize` is effectively ignored.

**Bounded (ArrayBlockingQueue):** Prevents resource exhaustion with a fixed
capacity. Once full, the executor spawns extra threads up to
`maximumPoolSize`.

**Direct handoff (SynchronousQueue):** Has no capacity — hands tasks
directly to threads. If none available, creates one (up to maximum). What
`newCachedThreadPool()` uses.

## Saturation policies (rejection handlers)

When pool and queue are both full, the executor must reject the task:

- **AbortPolicy (default):** Throws RejectedExecutionException
- **CallerRunsPolicy:** The submitting thread executes the task itself
  (natural back-pressure)
- **DiscardPolicy:** Silently drops the task
- **DiscardOldestPolicy:** Drops the oldest unhandled task and retries

## Production configuration

A common production pattern combines a bounded queue with CallerRunsPolicy
to create natural back-pressure. When the pool and queue are full, the
submitting thread runs the task itself, which slows the rate of new
submissions without dropping work.

```java
int cores = Runtime.getRuntime().availableProcessors();

ThreadPoolExecutor executor = new ThreadPoolExecutor(
    cores, // corePoolSize: Keep CPUs busy
    cores * 2, // maximumPoolSize: Allow some burst
    60L, TimeUnit.SECONDS, // keepAliveTime: Clean up extra threads
    new ArrayBlockingQueue<>(1000), // workQueue: Bounded to prevent OOM
    new ThreadFactoryBuilder().setNameFormat("orders-wp-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy() // Rejection: Submit thread handles it
);
```

Key choices:

- **Bounded queue** prevents OOM under sustained load
- **CallerRunsPolicy** applies back-pressure instead of dropping tasks
- **Custom thread names** make thread dumps readable
- **`cores * 2` maximum** allows burst capacity for mixed workloads

## Factory method risks

The Executors convenience methods hide configuration that causes problems
under load:

| Setting          | `newFixedThreadPool(n)`  | `newCachedThreadPool()`    | Custom safe pool        |
|------------------|--------------------------|----------------------------|-------------------------|
| Core threads     | `n`                      | 0                          | `n`                     |
| Max threads      | `n`                      | `Integer.MAX_VALUE`        | `m` (fixed limit)       |
| Queue type       | LinkedBlockingQueue      | SynchronousQueue           | ArrayBlockingQueue      |
| Queue capacity   | Unbounded                | 0 (direct handoff)         | Bounded (e.g. 1000)     |
| Rejection policy | AbortPolicy              | AbortPolicy                | CallerRunsPolicy        |
| Primary risk     | OOM from unbounded queue | Thread exhaustion on burst | Back-pressure on caller |

A fixed pool's unbounded queue can grow until the JVM runs out of memory. A
cached pool can spawn threads without limit during traffic spikes. Both fail
catastrophically under sustained load. The custom configuration in the
production example above avoids both failure modes.

## Related

- [Executor service](executor-service.md) - Thread pool abstraction
- [Fork join pool](fork-join-pool.md) - Work-stealing for recursive tasks
- [Thread pool sizing](thread-pool-sizing.md) - Optimal thread count formulas
- [Thread states](thread-states.md) - Diagnosing pool worker states

---

Return to [Concurrency](_index.md)
