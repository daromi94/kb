# Future

A Future is a placeholder for the result of an asynchronous computation. It
decouples task submission from result retrieval — submit a Callable to an
ExecutorService, get a Future back immediately, and retrieve the result later.

## Workflow

```java
Future<Integer> future = executor.submit(() -> performLongTask());

// Main thread continues other work...

Integer result = future.get(); // blocks until ready
```

The executor assigns the task to a worker thread. The calling thread is free
to do other work until it calls `get()`.

## Methods

**`get()`:** Blocks until the result is ready. Throws InterruptedException if
the waiting thread is interrupted, ExecutionException if the task threw an
exception.

**`get(long timeout, TimeUnit unit)`:** Same as `get()` but throws
TimeoutException if the result is not ready within the specified window.
Prevents indefinite blocking.

**`isDone()`:** Non-blocking check for whether the task has finished
(successfully, exceptionally, or by cancellation).

**`cancel(boolean mayInterruptIfRunning)`:** Attempts to cancel the task. If
the task has not started, it should never run. If it is running, the
`mayInterruptIfRunning` flag determines whether the worker thread is
interrupted.

## Callable vs Runnable

Runnable has two limitations that Future and Callable solve:

- **No return value:** `run()` is void. Getting data out requires shared
  mutable state, introducing safety hazards
- **No checked exceptions:** Errors inside `run()` cannot propagate to the
  submitting thread

Callable returns a value and throws checked exceptions. The Future
encapsulates both the result and the failure.

## The blocking limitation

`get()` is a blocking operation. Processing 100 futures requires calling
`get()` sequentially or polling `isDone()`. There is no way to say "when
this future completes, run that task automatically."

## Related

- [CompletableFuture](completable-future.md) - Non-blocking composition
- [Executor service](executor-service.md) - Thread pool abstraction
- [Safety and liveness](safety-and-liveness.md) - Blocking as a liveness risk

---

Return to [Concurrency](_index.md)
