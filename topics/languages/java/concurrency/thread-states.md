# Thread states

Java defines six thread states in the `Thread.State` enum. Understanding these
states is essential for reading thread dumps and diagnosing thread pool behavior.

## The six states

**NEW:** Thread object created but `start()` not yet called. The thread exists
in JVM memory but the OS has not allocated execution resources.

**RUNNABLE:** Executing in the JVM or ready to execute. The JVM considers a
thread runnable even if it is waiting for the OS scheduler to assign CPU
time—there is no distinction between "running" and "ready to run."

**BLOCKED:** Waiting to acquire a monitor lock to enter a `synchronized` block
or method. Only triggered by intrinsic locks — contention on ReentrantLock
shows as WAITING, not BLOCKED.

**WAITING:** Waiting indefinitely for another thread to perform an action.
Triggered by `Object.wait()`, `Thread.join()`, or `LockSupport.park()` without
a timeout.

**TIMED_WAITING:** Same as WAITING but with a deadline. Triggered by
`Thread.sleep(ms)`, `Object.wait(ms)`, `Thread.join(ms)`,
`LockSupport.parkNanos()`, or `LockSupport.parkUntil()`. Wakes on signal
or timeout, whichever comes first.

**TERMINATED:** The `run()` method completed normally or an uncaught exception
killed the thread. A terminated thread cannot be restarted—the pool must create
a new one.

## State transitions

```text
+-----+   start()   +----------+   run() ends   +------------+
| NEW | ----------> | RUNNABLE | -------------> | TERMINATED |
+-----+             +----+-----+                +------------+
                      |   |   |
         +------------+   |   +-------------+
         |                |                 |
         v                v                 v
   +-----------+    +-----------+    +-----------------+
   |  BLOCKED  |    |  WAITING  |    |  TIMED_WAITING  |
   +-----------+    +-----------+    +-----------------+

   All three return to RUNNABLE when their condition
   resolves: lock acquired, notify/unpark, or timeout.
```

Transitions into blocking states:

| Target state  | Trigger                                                              |
|---------------|----------------------------------------------------------------------|
| BLOCKED       | Entering `synchronized` when lock is held                            |
| WAITING       | `wait()` / `join()` / `park()` (no timeout)                          |
| TIMED_WAITING | `sleep(n)` / `wait(n)` / `join(n)` / `parkNanos(n)` / `parkUntil(n)` |

## Thread pool context

Thread states reveal what pool workers are doing:

| Worker state  | Meaning                                              |
|---------------|------------------------------------------------------|
| RUNNABLE      | Actively processing a task                           |
| WAITING       | Idle, blocked on `queue.take()` waiting for work     |
| TIMED_WAITING | Idle with `keepAliveTime`, blocked on `queue.poll()` |
| BLOCKED       | Contending on a `synchronized` lock inside a task    |

## Diagnostic patterns

**Many BLOCKED threads:** Workers are contending on `synchronized` locks,
creating a bottleneck. Consider replacing intrinsic locks with
`java.util.concurrent` alternatives.

**Most workers WAITING:** The pool is oversized for the current workload.
Threads sit idle on `queue.take()` with nothing to process.

**Frequent NEW-to-TERMINATED cycling:** The `keepAliveTime` is too short,
causing the pool to destroy and recreate threads instead of reusing them.

## Related

- [Threads](threads.md) - Thread fundamentals and creation
- [Thread pool executor](thread-pool-executor.md) - Pool configuration and behavior

---

Return to [Concurrency](_index.md)
