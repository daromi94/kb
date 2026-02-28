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

## Shutting down

ExecutorService does not stop when your code finishes. Worker threads are
user threads, so they keep the JVM alive. You must shut down explicitly:

- **`shutdown()`:** No new tasks accepted, but queued tasks finish
- **`shutdownNow()`:** Attempts to stop active tasks and returns queued tasks

## Example

```java
import java.util.concurrent.*;

public class ExecutorExample {
    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(3);

        Future<String> future = executor.submit(() -> {
            Thread.sleep(1000);
            return "Task Complete";
        });

        // Do other work here...

        System.out.println(future.get()); // Blocks until ready

        executor.shutdown();
    }
}
```

## Related

- [Thread pool executor](thread-pool-executor.md) - Fine-tuning thread pools
- [Fork join pool](fork-join-pool.md) - Work-stealing for recursive tasks
- [Thread pool sizing](thread-pool-sizing.md) - Optimal thread count formulas

---

Return to [Concurrency](_index.md)
