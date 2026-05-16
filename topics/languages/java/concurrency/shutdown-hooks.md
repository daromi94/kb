# Shutdown hooks

A shutdown hook is an unstarted Thread that the JVM starts during its
shutdown sequence. Applications use it to clean up before the process
exits.

## Registration

Register a hook by passing an unstarted Thread to
`Runtime.getRuntime().addShutdownHook`. Passing an already-started thread
throws IllegalArgumentException.

```java
public class Main {
    public static void main(String[] args) {
        Thread cleanup = new Thread(() -> {
            // Clean up
        });

        Runtime.getRuntime().addShutdownHook(cleanup);
    }
}
```

Deregister a hook with `removeShutdownHook(Thread)`; it returns `true`
if the hook was found and removed.

## Common uses

- **Draining:** Letting active requests or tasks complete before exit
- **Resource cleanup:** Closing database connections, network sockets,
  or open file streams
- **State saving:** Flushing in-memory buffers to disk or persisting
  session state
- **Housekeeping:** Deleting temporary files created during the run
- **Logging:** Recording the time and reason the application stopped

## When hooks run

The JVM starts the shutdown sequence on three triggers:

- The last non-daemon thread exits (normal completion)
- Code calls `System.exit(int)` or `Runtime.exit(int)`
- The OS delivers a termination signal

## When hooks are bypassed

Shutdown hooks are not a guarantee. They are skipped on abrupt
termination:

- `Runtime.halt(int)` exits immediately without initiating the shutdown
  sequence.
- The OS kills the process forcibly (SIGKILL, `kill -9`)
- A fatal JVM error or native crash aborts the process

## Concurrent execution

Multiple registered hooks start in an unspecified order and run
concurrently. Two consequences:

- Cleanup code must be thread-safe. A hook closing a connection pool
  cannot assume another hook isn't still writing through it.
- Hooks cannot rely on ordering. Don't register a logger-flush hook and
  expect it to run after a hook that produces final log lines.

## Time budget

The OS, not the JVM, owns the time budget. When the operating system
asks the process to terminate, it grants a limited window before
forcing termination. A slow hook is cut off mid-execution and the
process dies regardless of progress.

Keep work bounded: close handles, flush buffers, write a final log line.
Avoid network calls to unreliable endpoints, blocking operations without
timeouts, and any work that competes with other hooks for the same
resources.

## Limited environment

By the time a hook runs, the JVM is already winding down. A hook
can only depend on what it controls directly — its own captured state,
its own spawned threads, and basic JVM facilities — never on shared
application services.

---

Return to [Concurrency](_index.md)
