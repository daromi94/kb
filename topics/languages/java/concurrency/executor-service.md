# Executor service

ExecutorService decouples task submission from execution. Instead of creating
a thread per task, you submit tasks to a **thread pool** that reuses a set of
worker threads.

## Why use a thread pool

Calling `new Thread().start()` for every task has drawbacks:

- **Resource exhaustion:** Threads are expensive. Spawning thousands can crash
  an application by consuming too much stack space
- **Overhead:** Creating and destroying threads takes significant CPU time
- **Lack of control:** Hard to manage lifecycle — pausing, canceling, or
  limiting concurrent tasks

ExecutorService solves this with a **work queue** and a **thread pool**.

## Common executor types

The Executors factory provides pre-configured thread pool implementations:

| Pool type | Method                      | Behavior                            |
|-----------|-----------------------------|-------------------------------------|
| Fixed     | `newFixedThreadPool(n)`     | Set number of threads; tasks queue  |
| Cached    | `newCachedThreadPool()`     | Creates threads as needed, reclaims |
| Single    | `newSingleThreadExecutor()` | One thread, tasks run sequentially  |
| Scheduled | `newScheduledThreadPool(n)` | Delayed or periodic execution       |

## Task lifecycle

Submitting a task returns a Future — a placeholder for a result that has
not arrived yet.

1. **Submission:** Provide a Runnable (no return) or Callable (returns value)
2. **Execution:** A worker thread picks the task from the queue and runs it
3. **Completion:** Call `future.get()` to retrieve the result (blocks until
   done)

---

Return to [Concurrency](_index.md)
