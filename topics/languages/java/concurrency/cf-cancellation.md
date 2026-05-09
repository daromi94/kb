# CompletableFuture cancellation

Calling `cancel(true)` on a CompletableFuture does not interrupt the
thread executing the task. The `mayInterruptIfRunning` parameter is
ignored — CompletableFuture has no reference to the worker thread.
Cancellation is purely a state change: the future completes exceptionally
with a CancellationException, preventing downstream stages from running.

This makes `cancel(true)` a **logical** cancellation. To achieve
**physical** cancellation (stopping the thread), you need cooperative
patterns.

## Cooperative cancellation

Pass a shared AtomicBoolean into the pipeline. Each stage polls the
flag and throws CancellationException if set.

```java
CompletableFuture.supplyAsync(() -> {
    checkCancel(signal);
    return fetch(url);
}, executor)
.thenApplyAsync(data -> {
    for (int i = 0; i < batches; i++) {
        checkCancel(signal);
        process(data, i);
    }
    return data;
}, executor);
```

The check method:

```java
private void checkCancel(AtomicBoolean signal) {
    if (signal.get()) {
        throw new CancellationException();
    }
}
```

To trigger cancellation, set the flag and cancel the future:

```java
signal.set(true);
pipeline.cancel(true);
```

Setting the flag stops in-progress work. Calling `cancel(true)` prevents
stages that have not started from executing.

## Cancellation strategies

| Strategy       | Mechanism    | Stops running thread | Use case                  |
|----------------|--------------|----------------------|---------------------------|
| `cancel(true)` | State change | No                   | Result no longer needed   |
| AtomicBoolean  | Polling      | Yes (at checkpoint)  | CPU-intensive work        |
| Close resource | IOException  | Yes (immediately)    | Non-interruptible sockets |

---

Return to [Concurrency](_index.md)
