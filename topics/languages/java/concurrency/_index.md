# Concurrency

Java concurrency in practice.

## Notes

- [Concurrency](concurrency.md) - Handling multiple tasks with interleaving
- [Parallelism](parallelism.md) - Simultaneous execution across cores
- [Threads](threads.md) - Units of execution in Java
- [Thread states](thread-states.md) - The six JVM lifecycle states
- [Thread memory](thread-memory.md) - Shared vs. thread-private state
- [Daemon threads](daemon-threads.md) - Background service threads
- [Shutdown hooks](shutdown-hooks.md) - Cleanup callbacks at JVM exit
- [Safety and liveness](safety-and-liveness.md) - Wrong answer vs. no answer
- [Thread safety hazards](thread-safety-hazards.md) - Race conditions, visibility, and reordering
- [Interruption](interruption.md) - Cooperative thread cancellation
- [Concurrency models](concurrency-models.md) - Server I/O architecture patterns
- [Thread-per-client](thread-per-client.md) - Dedicated thread per connection
- [Blocking I/O](blocking-io.md) - Overlapping I/O waits with CPU work
- [I/O multiplexing](io-multiplexing.md) - select/poll and Java NIO
- [Executor service](executor-service.md) - Thread pool abstraction
- [Future](future.md) - Async result placeholder
- [CompletableFuture](completable-future.md) - Non-blocking async composition
- [CompletableFuture cancellation](cf-cancellation.md) - Stopping async pipelines
- [Thread pool executor](thread-pool-executor.md) - Fine-tuning thread pools
- [Fork join pool](fork-join-pool.md) - Work-stealing for recursive tasks
- [Thread pool sizing](thread-pool-sizing.md) - Optimal thread count formulas

---

Return to [Java](../_index.md)
