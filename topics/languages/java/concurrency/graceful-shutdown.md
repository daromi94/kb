# Graceful shutdown

A graceful shutdown is the sequence an application runs after a
termination signal: stop intake, drain in-flight work, release
resources, then exit. Skipping it drops work mid-execution — corrupted
writes, half-flushed buffers, and lost client responses.

A shutdown hook is only the *trigger* for this sequence. The execution
requires cooperation from every component that owns long-lived state,
holds resources, or runs worker threads.

## The four phases

1. **Stop intake.** Close listeners, return 503 on new requests, stop
   pulling from message queues. New work must not enter the system.
2. **Drain in-flight work.** Let active requests complete. Wait for
   queued tasks to finish, or cancel them if the deadline is approaching.
3. **Release resources.** Close pools, sockets, files, and database
   connections in the order that respects their dependencies.
4. **Exit.** Return from the hook. The JVM continues its shutdown
   sequence and the process terminates.

All four phases share one OS-imposed time budget. Plan each phase so
the slowest still fits.

## Delegate to a coordinator

Don't bury shutdown logic inside the hook itself. As the application
grows, the hook becomes a tangle of unrelated cleanup code with no clear
ordering or testing surface.

Introduce a lifecycle coordinator. Components register at startup; the
hook asks the coordinator to shut everything down.

```java
class Main {
    interface Lifecycle {
        void stop();
    }

    static class ShutdownCoordinator {
        private final List<Lifecycle> components = new CopyOnWriteArrayList<>();

        public void register(final Lifecycle c) {
            components.add(c);
        }

        public void shutdown() {
            for (int i = components.size() - 1; i >= 0; i--) {
                try {
                    final var component = components.get(i);

                    component.stop();
                } catch (Exception e) {
                    logger.warn("component failed to stop", e);
                }
            }
        }
    }

    public static void main(final String[] args) {
        final var coordinator = new ShutdownCoordinator();

        Runtime.getRuntime().addShutdownHook(new Thread(coordinator::shutdown));
    }
}
```

The coordinator enforces two properties:

- **Reverse-order shutdown.** Iterate from last to first so dependents
  stop before their dependencies. Shut the HTTP server before the thread
  pool it dispatches to; close the cache before the database it writes
  through to.
- **Isolation.** A failure in one component doesn't abort the rest of
  the cleanup.

## Failure modes

- **Daemon-owned state.** Daemons die when the JVM halts, regardless
  of in-flight work. Run components with cleanup obligations on user
  threads.
- **Unbounded waits.** `awaitTermination` and `join` block forever
  without a timeout — a single stuck task stalls the entire shutdown.
  Always pass an explicit timeout.
- **Cyclic dependencies.** If A's shutdown calls into B and B's
  shutdown calls into A, neither finishes.

---

Return to [Concurrency](_index.md)
