# BIO scaling walls

The blocking I/O (BIO) thread-per-connection model was the standard way to
handle networking in Java before NIO. It assigns a dedicated thread to each
client socket, following a synchronous lifecycle: `accept()` blocks waiting
for a connection, a new thread is spawned for the socket, `readLine()`
blocks waiting for data, the thread processes and writes back, then waits
again. This model hits three scaling walls that frameworks like Netty were
built to overcome.

## Resource wastage

Network I/O is slow compared to CPU speeds. In a BIO model a thread might
spend 99% of its life waiting for packets to arrive over the wire. With
10,000 threads, 9,900 of them are dormant yet still managed by the OS
scheduler, consuming resources without performing useful work.

## Memory footprint

Every Java thread requires its own stack memory. At the default 1MB stack
size on 64-bit JVMs, the arithmetic is straightforward:

```
10,000 connections x 1MB per thread = 10GB RAM
```

This is stack memory alone, before accounting for the heap or application
data. This makes the thread-per-connection model impractical for the C10K
problem — handling 10,000 concurrent connections.

## Context switching overhead

The OS CPU scheduler must constantly swap which thread runs on the physical
cores. As thread count grows, the CPU spends more time saving and loading
thread states than executing business logic. This results in thrashing,
where system throughput collapses even though the CPU is not fully utilized
by application code.

## The NIO alternative

Java NIO (introduced in JDK 1.4) addresses these walls by decoupling
threads from connections. It rests on two pillars:

**Non-blocking sockets:** Calling `read()` on a non-blocking socket returns
immediately with `EAGAIN` if no data is available, freeing the thread for
other work.

**I/O multiplexing:** A Selector monitors thousands of sockets and wakes
the thread only when at least one has data ready, avoiding both busy-waiting
and per-connection thread allocation.

| Concept        | Blocking I/O (BIO)      | Non-blocking I/O (NIO)      |
|----------------|-------------------------|-----------------------------|
| Data flow      | Streams (byte by byte)  | Buffers (block of data)     |
| Thread usage   | 1 thread = 1 connection | 1 thread = many connections |
| OS interaction | Blocking syscalls       | Event-based notifications   |

## Related

- [Netty](netty.md) - Framework built to abstract NIO complexity
- [Non-blocking sockets](non-blocking-sockets.md) - How non-blocking mode
  works at the OS level
- [Selector](selector.md) - The multiplexer that replaces per-connection
  threads

---

Return to [Netty](_index.md)
