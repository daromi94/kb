# I/O multiplexing

I/O multiplexing allows a single thread to monitor multiple file descriptors
(sockets) simultaneously, dispatching work only when data is actually ready.
It was developed to bypass the thread-per-connection bottleneck when OS threads
were too expensive to scale.

## System calls

Instead of one thread blocking on one socket, multiplexing system calls let a
thread hand a set of file descriptors to the kernel and block until at least
one has data ready.

**`select`:** Takes three sets of file descriptors (read, write, exception).
The kernel scans the entire set on each call, making it O(n) per invocation.
Limited to a fixed maximum number of descriptors (typically 1,024 on Linux).

**`poll`:** Replaces the fixed-size bitmask with an array of `pollfd` structs,
removing the descriptor limit. Still O(n) per call since the kernel scans the
full array.

**`epoll` (Linux) / `kqueue` (BSD/macOS):** Event-driven alternatives that
register interest once and receive only the descriptors that are ready. O(1)
per ready event, scaling to hundreds of thousands of connections.

## Java NIO

`java.nio` wraps OS multiplexing facilities into two abstractions:

**Channel:** A bidirectional connection to a file descriptor (e.g.,
SocketChannel, ServerSocketChannel). Channels can be set to non-blocking
mode, where read/write calls return immediately if no data is available.

**Selector:** A multiplexer that monitors registered channels. Calling
`selector.select()` blocks until at least one channel is ready, then returns
a set of selection keys identifying those channels.

Here's an example:

```java
Selector selector = Selector.open();
ServerSocketChannel server = ServerSocketChannel.open();
server.configureBlocking(false);
server.bind(new InetSocketAddress(8080));
server.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // blocks until at least one channel is ready
    Set<SelectionKey> keys = selector.selectedKeys();
    for (SelectionKey key : keys) {
        if (key.isAcceptable()) {
            SocketChannel client = server.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // read data from the channel
        }
    }
    keys.clear();
}
```

## Reactor pattern

The Reactor pattern structures NIO applications around a single event loop
(the "Reactor" thread) that demultiplexes I/O events and dispatches them to
handlers.

```text
+------------------+      +-----------+
| Selector         |      | Worker    |
| (Reactor thread) |----->| Pool      |
|                  |      |           |
| select() loop    |      | Processes |
| dispatches ready |      | data once |
| channels         |      | available |
+------------------+      +-----------+
        ^
        |  register
   +----+----+----+--+
   | Ch1 | Ch2 | Ch3 |  (thousands of channels)
   +-----+----+------+
```

The Reactor thread handles accept and read-readiness events. When data is
available, it dispatches the actual processing to a worker thread pool,
keeping the event loop unblocked.

## Trade-offs

Multiplexed I/O achieves high connection counts with few threads, but at the
cost of programming complexity. Application logic must be expressed as state
machines or callbacks rather than sequential code, since a single thread
interleaves work across many connections.

## Related

- [Blocking I/O](blocking-io.md) - The synchronous model that multiplexing replaces
- [Concurrency models](concurrency-models.md) - Server I/O architecture evolution

---

Return to [Concurrency](_index.md)
