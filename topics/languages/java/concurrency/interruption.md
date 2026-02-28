# Interruption

Interruption is a cooperative mechanism for signaling a thread to stop what
it is doing. It is a request, not a preemptive kill. Every thread has an
**interrupt status** — a boolean flag that is set to `true` when the thread
is interrupted.

Threads own their own execution. One thread cannot force another to stop.
Thread A sets the interrupt flag on Thread B, and Thread B periodically
checks that flag and decides how to respond.

## Blocked vs. active threads

The mechanism works differently depending on thread state.

**Blocked thread.** When a thread calls a blocking method like
`Thread.sleep(1000)`, it enters a waiting state. If another thread calls
`interrupt()` on it, the JVM sets the interrupt bit, notices the thread is
in a stoppable state, wakes it, clears the flag, and throws
InterruptedException.

**Active thread.** If a thread is running a tight loop, setting the
interrupt flag does nothing automatically. The thread continues forever
unless it explicitly checks. Use the flag as the loop guard:

```java
while (!Thread.currentThread().isInterrupted()) {
    computeNextChunk();
}
```

`isInterrupted()` is an instance method that reads the flag without
clearing it. `Thread.interrupted()` is a static method that reads and
clears — only use it when you intend to consume the signal.

## Handling the flag

A common mistake is swallowing interruptions.

**Propagation.** If you catch InterruptedException, the best response is
to throw it up the stack. This lets the caller — who owns the thread
policy — decide what to do.

```java
public void myMethod() throws InterruptedException {
    Thread.sleep(1000);
}
```

**Restoration.** If your method cannot throw the exception (e.g., it
implements Runnable), you must restore the interrupt status. The JVM
clears the flag when it throws the exception, so failure to re-interrupt
loses the cancellation signal permanently.

```java
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

## I/O interruptibility

Not all I/O responds to interruption.

**`java.io` (blocking I/O).** Methods like `InputStream.read()` on a
plain Socket are not interruptible for platform threads. Calling
`interrupt()` has no effect — the only escape is closing the underlying
socket. Virtual threads are the exception: interrupting a virtual thread
blocked on a socket read wakes it and throws SocketException.

**`java.nio` (interruptible channels).** Classes implementing
InterruptibleChannel (like SocketChannel) throw
ClosedByInterruptException and close the channel if the thread is
interrupted while blocked on I/O.

## Cleanup

Use `try-finally` to release resources regardless of whether a task
completes normally or via interruption.

```java
lock.lock();
try {
    while (!Thread.currentThread().isInterrupted()) {
        doWork();
    }
} finally {
    lock.unlock();
}
```

## JVM internals

`Thread.interrupt()` is implemented entirely within the JVM's threading
library. It does not rely on OS signals. On POSIX systems, it uses
`pthread_cond_signal` to nudge the thread out of its waiting state.

## Related

- [Thread states](thread-states.md) - The six JVM lifecycle states
- [Safety and liveness](safety-and-liveness.md) - Liveness failures from blocking
- [Executor service](executor-service.md) - Thread pool abstraction

---

Return to [Concurrency](_index.md)
