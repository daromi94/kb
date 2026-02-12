# Concurrency

Java concurrency in practice.

## Notes

- [Concurrency](concurrency.md) - Handling multiple tasks with interleaving
- [Parallelism](parallelism.md) - Simultaneous execution across multiple cores
- [Concurrency models](concurrency-models.md) - Thread-per-client, NIO, and modern virtual thread architectures
- [Thread-per-client](thread-per-client.md) - Dedicated thread per connection workflow and trade-offs
- [Blocking I/O](blocking-io.md) - Overlapping I/O waits with productive CPU work
- [I/O multiplexing](io-multiplexing.md) - select/poll and Java NIO Selector/Channel
- [Threads](threads.md) - Units of execution in Java
- [Thread memory](thread-memory.md) - Shared vs. thread-private state in the JVM
- [Thread safety hazards](thread-safety-hazards.md) - Race conditions, visibility, and reordering
- [Daemon threads](daemon-threads.md) - Background service threads
- [Thread states](thread-states.md) - The six JVM thread lifecycle states
- [Executor service](executor-service.md) - Thread pool abstraction
- [Thread pool executor](thread-pool-executor.md) - Fine-tuning thread pools
- [Fork join pool](fork-join-pool.md) - Work-stealing for recursive tasks
- [Thread pool sizing](thread-pool-sizing.md) - Optimal thread count formulas

---

Return to [Java](../_index.md)
