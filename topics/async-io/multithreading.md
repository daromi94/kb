# Multithreading

Multithreading achieves concurrency by spinning up multiple threads within a
single process to handle multiple tasks at once.

## Characteristics

**Concurrency within a process:** Instead of one main thread, you create
several threads that execute code independently.

**Shared memory:** Unlike multi-processing, all threads within a process share
the same memory and resources. This makes them fast and efficient for
communication.

**Challenges:** Shared memory introduces the risk of race conditions, where
multiple threads try to modify the same data simultaneously. Developers must
write thread-safe code using tools like mutexes (locks).

## Best use case

Often used to handle multiple client connections or tasks where low latency and
high-speed data sharing between tasks are required.

## Related

- [Threads are evil](threads-are-evil.md) - Why multithreading is dangerous
- [Async I/O vs multithreading](async-vs-multithreading.md) - Comparison of
  approaches
