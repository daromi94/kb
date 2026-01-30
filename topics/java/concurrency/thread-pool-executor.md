# Thread pool executor

`ThreadPoolExecutor` is the extensible, low-level implementation of
`ExecutorService`. While the `Executors` factory provides pre-configured pools,
`ThreadPoolExecutor` allows fine-tuning exactly how threads are created, how
many can exist, and how they behave under heavy load.

## Internal mechanism

When a task is submitted via `execute(Runnable)`:

1. **Core pool size:** If fewer than `corePoolSize` threads are running, create
   a new thread to run the task, even if other workers are idle
2. **The queue:** If `corePoolSize` or more threads are running, place the task
   in the `BlockingQueue`
3. **Maximum pool size:** If the queue is full and fewer than `maximumPoolSize`
   threads are running, create a new non-core thread
4. **Rejection:** If the queue is full and `maximumPoolSize` threads are already
   running, pass the task to a `RejectedExecutionHandler`

## Core parameters

| Parameter           | Purpose                                                      |
|---------------------|--------------------------------------------------------------|
| **corePoolSize**    | Threads to keep in the pool, even if idle                    |
| **maximumPoolSize** | Absolute ceiling on threads allowed                          |
| **keepAliveTime**   | How long excess threads (above core) wait before terminating |
| **workQueue**       | Queue holding tasks before execution                         |

## Queue types

The behavior changes drastically based on the queue:

**Unbounded (`LinkedBlockingQueue`):** What `newFixedThreadPool` uses. The queue
grows indefinitely. The pool never exceeds `corePoolSize`, and `maximumPoolSize`
is effectively ignored.

**Bounded (`ArrayBlockingQueue`):** Prevents resource exhaustion with a fixed
capacity. Once full, the executor spawns extra threads up to `maximumPoolSize`.

**Direct handoff (`SynchronousQueue`):** Has no capacity—hands tasks directly to
threads. If none available, creates one (up to maximum). What
`newCachedThreadPool` uses.

## Saturation policies (rejection handlers)

When pool and queue are both full, the executor must reject the task:

- **AbortPolicy (default):** Throws `RejectedExecutionException`
- **CallerRunsPolicy:** The submitting thread executes the task itself (natural
  back-pressure)
- **DiscardPolicy:** Silently drops the task
- **DiscardOldestPolicy:** Drops the oldest unhandled task and retries

## When to use ThreadPoolExecutor directly

Use it over the standard `Executors` factory when you need to:

- Enforce strict resource constraints (limit queue size to prevent OOM)
- Set a specific `ThreadFactory` for custom thread names and priorities
- Choose a bounded queue with a specific rejection policy
