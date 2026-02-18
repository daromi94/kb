# Transport

A transport is the mechanism Netty uses to move data across the network (or
within a JVM). In standard Java, blocking and non-blocking I/O have completely
different APIs — switching from `java.net` to `java.nio` typically requires a
full rewrite. Netty solves this by layering a single API over all transport
implementations, so application code always works with Channel,
ChannelPipeline, and ChannelHandler regardless of the underlying I/O model.

## Switching transports

Because the transport is an implementation detail hidden behind Netty's
abstractions, switching between I/O mechanisms reduces to swapping the
`IoHandlerFactory` and Channel class in the bootstrap configuration:

```java
// NIO
var group = new MultiThreadIoEventLoopGroup(NioIoHandler.newFactory());
bootstrap.group(group).channel(NioServerSocketChannel.class);

// Epoll (Linux)
var group = new MultiThreadIoEventLoopGroup(EpollIoHandler.newFactory());
bootstrap.group(group).channel(EpollServerSocketChannel.class);
```

`MultiThreadIoEventLoopGroup` is the unified EventLoopGroup implementation
for all transports. The `IoHandlerFactory` argument selects which I/O
mechanism to use. The rest of the application — handlers, pipeline, business
logic — remains untouched.

## Available transports

| Transport | Package                       | Use case                             |
|-----------|-------------------------------|--------------------------------------|
| NIO       | `io.netty.channel.socket.nio` | High-concurrency, scalable servers   |
| Epoll     | `io.netty.channel.epoll`      | Linux-optimized high performance     |
| KQueue    | `io.netty.channel.kqueue`     | macOS/BSD-optimized high performance |
| io_uring  | `io.netty.channel.uring`      | Linux completion-based I/O           |
| OIO       | `io.netty.channel.socket.oio` | Deprecated — use NIO or native       |
| Embedded  | `io.netty.channel.embedded`   | Unit testing ChannelHandlers         |

**NIO** is the default choice for production. It uses I/O multiplexing via a
Selector, allowing a small number of threads to manage thousands of
connections.

**Epoll** uses JNI to call Linux's `epoll()` directly, bypassing the JDK's
NIO layer. It is faster than the NIO transport, fully non-blocking, and
exposes Linux-specific socket options like `SO_REUSEPORT`.

**KQueue** is the macOS/BSD equivalent of Epoll. It uses JNI to call
`kqueue()` directly, offering the same performance benefits on those
platforms.

**io_uring** uses Linux's completion-based I/O interface. Where Epoll is
readiness-based (tells you a socket is ready, then you perform the I/O),
io_uring is completion-based (you submit I/O, the kernel notifies you
when it finishes). Requires a recent Linux kernel.

**OIO** wraps the classic `java.net` blocking sockets. Deprecated — use NIO,
Epoll, or KQueue instead.

**Embedded** provides a test harness that drives data through a pipeline
in-process, allowing assertions on handler output without binding to a real
port.

## Related

- [Bootstrap](bootstrap.md) - Where the transport is configured
- [Channel](channel.md) - The I/O conduit abstraction transports implement
- [BIO scaling walls](bio-scaling-walls.md) - Why blocking transport fails
  at scale
- [Event loop](event-loop.md) - Thread model tied to transport choice

---

Return to [Netty](_index.md)
