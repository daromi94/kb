# Executor service

The `ExecutorService` is a higher-level API that decouples task submission from
task execution. Instead of creating a new thread for every task, you submit
tasks to a **thread pool** which manages a set of worker threads that are reused
to execute those tasks.

## Why use an ExecutorService

Manually calling `new Thread().start()` for every task has drawbacks:

- **Resource exhaustion:** Threads are expensive. Spawning thousands can crash
  an application by consuming too much memory (stack space)
- **Overhead:** Creating and destroying threads takes significant CPU time
- **Lack of control:** Hard to manage lifecycle—pausing, canceling, or limiting
  concurrent tasks

The `ExecutorService` solves this with a **work queue** and a **thread pool**.

## Common executor types

The `Executors` factory provides pre-configured thread pool implementations:

| Pool type              | Method                      | Behavior                            |
|------------------------|-----------------------------|-------------------------------------|
| **Fixed thread pool**  | `newFixedThreadPool(n)`     | Set number of threads; tasks queue  |
| **Cached thread pool** | `newCachedThreadPool()`     | Creates threads as needed, reclaims |
| **Single thread**      | `newSingleThreadExecutor()` | One thread, tasks run sequentially  |
| **Scheduled pool**     | `newScheduledThreadPool(n)` | Delayed or periodic execution       |

## Task lifecycle

When you submit a task, you get a **`Future`** object—a placeholder for a result
that hasn't arrived yet.

1. **Submission:** Provide a `Runnable` (no return) or `Callable` (returns value)
2. **Execution:** A worker thread picks the task from the queue and runs it
3. **Completion:** Call `future.get()` to retrieve the result (blocks until done)

## Shutting down

An `ExecutorService` won't stop automatically when your code finishes. The
worker threads are user threads, so they keep the JVM alive. You must explicitly
shut it down:

- **`shutdown()`:** Graceful shutdown. No new tasks accepted, but existing tasks
  (including queued ones) will finish
- **`shutdownNow()`:** Attempts to stop active tasks and ignores queued tasks

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
