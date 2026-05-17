# Executor service shutdown

An ExecutorService must be shut down explicitly so in-flight tasks can
drain and queued ones are accounted for.

## Three methods

- **`shutdown()`:** Stop accepting new tasks; queued tasks still run to
  completion.
- **`shutdownNow()`:** Interrupt active workers and return the list of
  tasks that were still queued (never started).
- **`awaitTermination(timeout, unit)`:** Block until all tasks finish or
  the timeout elapses. Returns `true` if the pool terminated.

`shutdownNow` cannot force a running task to stop — it only sets the
worker's interrupt flag. Tasks that ignore interrupts keep running
until they finish on their own.

## The two-phase idiom

Request a graceful shutdown first and wait. If the deadline passes,
escalate by interrupting the workers.

```java
class Main {
    public static void main(final String[] args) {
        final var executor = Executors.newFixedThreadPool(4);

        // Stop accepting new tasks; let in-flight ones run
        executor.shutdown();

        try {
            // Wait for graceful completion
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                // Deadline passed: interrupt the workers
                executor.shutdownNow();

                // Wait again in case tasks ignore the interrupt
                if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                    log.warn("executor did not terminate");
                }
            }
        } catch (final InterruptedException e) {
            // Caller was interrupted while waiting; escalate and restore the flag
            executor.shutdownNow();

            Thread.currentThread().interrupt();
        }
    }
}
```

The second `awaitTermination` matters because `shutdownNow` only sets
the interrupt flag — it doesn't stop the worker. A task that ignores
the flag keeps running, and the second wait catches that instead of
letting the pool hang silently.

The catch block handles the other case: the caller itself getting
interrupted while waiting. Escalate immediately, then restore the flag
so callers higher up still see the cancellation.

## What happens to tasks

| Phase                 | New submissions | Queued tasks | Active tasks |
|-----------------------|-----------------|--------------|--------------|
| Before shutdown       | Accepted        | Run normally | Run normally |
| After `shutdown()`    | Rejected        | Still run    | Continue     |
| After `shutdownNow()` | Rejected        | Returned     | Interrupted  |

New submissions after `shutdown()` throw RejectedExecutionException.
Tasks returned from `shutdownNow()` are the caller's responsibility —
typically discarded, logged, or re-submitted to another executor.

---

Return to [Concurrency](_index.md)
