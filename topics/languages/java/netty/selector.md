# Selector

The Selector is the core mechanism enabling the shift from thread-per-
connection to event-driven I/O. It allows one thread to monitor thousands
of sockets by delegating readiness tracking to the operating system.

## How it works

Instead of each thread blocking on its own socket, all sockets (Channels)
are registered with a single Selector. Calling `selector.select()` blocks
the thread, but it blocks on all registered channels simultaneously. When
at least one channel is ready for an operation — a new connection, data
arrival, or buffer availability — the Selector wakes the thread and returns
a set of SelectionKeys identifying the ready channels.

## Efficiency gains

**Fewer threads, more connections:** A single thread can monitor thousands
of sockets, eliminating the 1:1 thread-to-connection mapping. This removes
the massive memory overhead of per-thread stacks and drastically reduces
context switching.

**Thread retargeting:** In a blocking model a thread is stuck to a socket
until I/O completes. In the NIO model the thread is only active when there
is actual work to do. When no data is arriving, the thread is free to
handle events for other connections.

## Multiplexing API evolution

The efficiency of Java NIO depends on which underlying OS system call the
Selector uses:

**`select()` / `poll()`:** The kernel scans every registered socket to find
which are ready. This is O(n) per invocation and degrades as connection
count grows.

**`epoll` (Linux) / `kqueue` (BSD/macOS):** Event-driven APIs where the OS
maintains a list of ready sockets and hands it over on request. O(1) per
ready event, scaling to millions of connections.

## Why Netty wraps the Selector

While the Selector concept is simple, production use of the raw Java NIO
API exposes several edge cases:

**The epoll bug:** A long-standing JDK bug where the Selector enters a
busy-wait loop, consuming 100% CPU even with no I/O events pending. Netty
detects this condition and rebuilds the Selector automatically.

**Partial reads and writes:** Data rarely arrives as a complete message.
Managing buffers, flipping them correctly, and tracking state across
multiple `select()` cycles requires careful bookkeeping.

**Thread safety:** Ensuring the Selector and its associated Channels are
accessed safely across different threads is complex and prone to race
conditions.

**Backpressure:** Managing data flow so a fast sender does not overwhelm a
slow receiver is difficult to implement from scratch.

Netty provides a consistent, high-performance wrapper that handles state
management, buffer pooling, and OS-specific quirks so application code can
focus on business logic.

## Related

- [Non-blocking sockets](non-blocking-sockets.md) - The socket mode that
  requires a Selector
- [Netty](netty.md) - The framework that wraps Selector complexity
- [Partial I/O](partial-io.md) - One of the key challenges Selectors
  introduce

---

Return to [Netty](_index.md)
