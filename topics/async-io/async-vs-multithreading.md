# Async I/O vs multithreading

A comparison of two concurrency approaches: asynchronous I/O and multithreading.

## Threading and resource usage

| Aspect            | Async I/O       | Multithreading              |
|-------------------|-----------------|-----------------------------|
| Threads           | Single thread   | Multiple threads            |
| Memory            | Low (one stack) | Higher (stack per thread)   |
| Context switching | None            | OS switches between threads |

## Execution model

**Async I/O (non-blocking):** When the program starts an I/O task, it doesn't
wait. It provides a callback or promise and moves to the next task. When done,
the system notifies the thread to run the callback.

**Multithreading (concurrent):** Each thread handles its own task. If a thread
encounters an I/O operation, that thread might block, but other threads
continue running.

## Data safety and complexity

**Async I/O:** Safer and easier to reason about because only one piece of code
runs at any given time on that single thread. No risk of two things changing
the same variable simultaneously.

**Multithreading:** More complex because threads share memory. This leads to
race conditions where two threads update the same data at once. Requires locks
or mutexes, which can slow the program and cause deadlocks.

## Best use cases

| Approach       | Best for                                                 |
|----------------|----------------------------------------------------------|
| Async I/O      | I/O-bound tasks (databases, APIs, file systems)          |
| Multithreading | Concurrent independent operations with shared data needs |

For heavy CPU-bound tasks, multiprocessing is often better than either
approach.

## Related

- [Asynchronous I/O](asynchronous-io.md) - The non-blocking model
- [Multithreading](multithreading.md) - The concurrent threads model
- [Threads are evil](threads-are-evil.md) - Problems with multithreading
