# Call stack illusion

Call stacks are thread-local. They do not model asynchronous call chains,
and their error-handling semantics break down the moment work is
delegated to another thread.

## Exceptions cannot cross threads

When a caller delegates work to a background thread (typically by
placing a task on a shared queue), it gives up the call stack. If the
worker thread fails, the exception propagates to the worker's own
exception handler — the caller is never notified.

```text
Caller thread        Shared queue       Worker thread
     |                   |                   |
     |--- put task ----->|                   |
     |   (moves on)      |--- pick up ------>|
     |                   |                   X exception!
     |                   |          propagates to worker's
     |                   |          handler, not caller
     |  never notified   |                   |
```

Failure notification requires an explicit side-channel — for example,
writing an error code where the caller expects a result. Without this,
the failure is silent and the task is lost. This is directly analogous
to message loss in networked systems.

## Thread death loses in-flight work

When a bug causes an exception to bubble up to a thread's root, the
thread shuts down. The task it was processing is gone — unwound from the
call stack and already removed from the input queue. The message is lost
even though no network was involved.

This raises two questions with no good call-stack-based answers:

- **Who restarts the service** the dead thread was hosting?
- **How is it restored** to a known-good state?

## Failures become part of the model

With task-delegating concurrency, call-stack error handling is
insufficient. Systems must instead:

- Signal errors explicitly through messages, not exceptions
- Handle service faults and provide principled recovery
- Accept that tasks may be lost during restarts
- Use timeouts for response deadlines, since responses may be delayed
  by queued work, GC pauses, or other factors

These requirements are identical to those of distributed systems.
Concurrency within a single machine and communication across a network
demand the same failure model.

## Related

- [Supervision](supervision.md) - The fault-handling mechanism that
  replaces call-stack error propagation
- [Shared memory illusion](shared-memory-illusion.md) - The hardware
  argument for message passing
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) -
  The OOP argument for actors

---

Return to [Pekko](_index.md)
