# Shutdown hooks

A shutdown hook is an initialized but unstarted Thread registered with the
JVM. The JVM runs it during the shutdown sequence, giving an application
a final chance to release resources, flush state, or log termination
before the process exits.

## Registration

Register a hook through Runtime. The argument must be a constructed but
unstarted Thread — passing an already-started thread throws
IllegalArgumentException.

```java
public class Main {
    public static void main(String[] args) {
        Thread cleanup = new Thread(() -> {
            closeConnections();
            flushBuffers();
        });

        Runtime.getRuntime().addShutdownHook(cleanup);
    }
}
```

A previously registered hook can be removed with
`removeShutdownHook(Thread)`, which returns `true` if the hook was found
and deregistered.

## When hooks run

The JVM starts the shutdown sequence on three triggers:

- The last non-daemon thread exits (normal completion).
- Code calls `System.exit(int)` or `Runtime.exit(int)`.
- The OS delivers a termination signal — for example, SIGINT from Ctrl+C
  on the console, or SIGTERM on system shutdown.

## When hooks are bypassed

Shutdown hooks are not a guarantee. They are skipped on abrupt
termination:

- `Runtime.halt(int)` exits immediately without initiating the shutdown
  sequence.
- The OS kills the process forcibly (SIGKILL, `kill -9`) — user-space
  code does not get to run.
- A fatal JVM error or native crash aborts the process.

## Concurrent execution

Multiple registered hooks are started in an unspecified order and then
run concurrently. Two consequences:

- Cleanup code must be thread-safe. A hook closing a connection pool
  cannot assume another hook isn't still writing through it.
- Hooks cannot rely on ordering. Don't register a logger-flush hook and
  expect it to run after a hook that produces final log lines.

## Time budget

The OS, not the JVM, owns the time budget. When the operating system
asks the process to terminate, it grants a limited window before
forcing termination. A slow hook is interrupted mid-execution and the
process dies regardless of progress.

Keep work bounded: close handles, flush buffers, write a final log line.
Avoid network calls to unreliable endpoints, blocking operations without
timeouts, and any work that competes with other hooks for the same
resources.

## Limited environment

By the time a hook runs, the JVM is already winding down. Daemon threads
have been left to die, frameworks may be half-disposed, and other hooks
are executing in parallel. A hook can only depend on what it controls
directly — its own captured state, its own spawned threads, and basic
JVM facilities — never on shared services that the application has been
managing.

---

Return to [Concurrency](_index.md)
