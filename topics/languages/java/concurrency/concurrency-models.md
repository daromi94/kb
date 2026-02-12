# Concurrency models

Server concurrency has evolved through three architectural phases, driven by
changes in OS kernel capabilities and JVM design.

## Thread-per-client (classic)

The simplest model: each incoming connection gets a dedicated thread that
handles the full request lifecycle using blocking I/O. Code reads
sequentially, making it easy to write, debug, and reason about.

This model hit a wall when OS threads were expensive. Early Linux kernels
using the `LinuxThreads` library had high thread-creation costs, O(n)
schedulers that slowed as thread count grew, and per-thread stacks (typically
1MB) that exhausted memory at thousands of connections.

## Multiplexed I/O (NIO)

To work around thread limits, applications moved to I/O multiplexing. A small
number of threads—often just one Reactor thread plus a worker pool—manage
thousands of connections using `select`, `poll`, or `epoll` via Java NIO's
Selector and Channel abstractions.

This solved the scalability problem but introduced significant complexity.
Application logic becomes fragmented across callbacks and state machines,
making code harder to write, test, and debug.

## Thread-per-client (modern)

Several advances have made thread-per-client viable again at high scale:

**NPTL (Native POSIX Thread Library):** Replaced `LinuxThreads` in Linux 2.6,
drastically reducing thread creation and synchronization overhead.

**O(log n) schedulers:** The Completely Fair Scheduler (CFS) in Linux 2.6.23
uses a red-black tree, making scheduling cost nearly independent of thread
count.

**64-bit address spaces:** Modern systems have vast virtual address spaces,
and JVMs use guard pages and flexible stack management to reduce wasted memory
for idle threads.

**Virtual threads (Project Loom):** Introduced in JDK 21, virtual threads are
managed by the JVM and multiplexed onto a small carrier thread pool. They
restore sequential programming style while the runtime handles the
multiplexing transparently.

## The core difference

The fundamental distinction is how the application waits for data.

**Thread-per-client:** Each thread is dedicated to one connection. When the
client has no data ready, the thread calls `read()` and the OS suspends it.
The thread sits idle—consuming stack memory and a scheduling slot—until
packets arrive.

**I/O multiplexing:** A single thread monitors many connections through a
Selector. It asks the OS "which of these 1,000 sockets have data ready?"
and sleeps until the OS wakes it with a set of ready descriptors. The thread
only touches connections that have actual work, then returns to monitoring.

## Comparison

| Model                    | Resource usage    | Code complexity | Best for                          |
|--------------------------|-------------------|-----------------|-----------------------------------|
| Thread-per-client        | High (1MB/thread) | Low             | Low to medium concurrency         |
| NIO (multiplexed)        | Low (few threads) | High            | High concurrency, chatty I/O      |
| Modern thread-per-client | Low to moderate   | Low             | High-scale servers, microservices |

## Related

- [Thread-per-client](thread-per-client.md) - Workflow and benefits of the dedicated-thread model
- [Threads](threads.md) - Platform threads vs. virtual threads
- [Blocking I/O](blocking-io.md) - Why blocking creates a 1:1 thread-to-request mapping
- [I/O multiplexing](io-multiplexing.md) - select/poll/epoll and Java NIO mechanics
- [Thread pool sizing](thread-pool-sizing.md) - Sizing pools for each model

---

Return to [Concurrency](_index.md)
