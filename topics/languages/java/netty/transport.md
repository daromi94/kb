# Transport

A transport is the mechanism Netty uses to move data across the network (or
within a JVM). In standard Java, blocking and non-blocking I/O have completely
different APIs — switching from `java.net` to `java.nio` typically requires a
full rewrite. Netty solves this by layering a single API over all transport
implementations, so application code always works with Channel,
ChannelPipeline, and ChannelHandler regardless of the underlying I/O model.

## Switching transports

Because the transport is an implementation detail hidden behind Netty's
abstractions, migrating from blocking to non-blocking I/O reduces to swapping
the EventLoopGroup and Channel class in the bootstrap configuration:

```java
// Blocking (OIO)
bootstrap.group(oioGroup).channel(OioServerSocketChannel.class)

// Non-blocking (NIO)
bootstrap.group(nioGroup).channel(NioServerSocketChannel.class)
```

The rest of the application — handlers, pipeline, business logic — remains
untouched. This is in sharp contrast to raw JDK code, where the OIO and NIO
versions of the same program share almost no structure.

## Available transports

| Transport | Package                       | Use case                             |
|-----------|-------------------------------|--------------------------------------|
| NIO       | `io.netty.channel.socket.nio` | High-concurrency, scalable servers   |
| Epoll     | `io.netty.channel.epoll`      | Linux-optimized high performance     |
| KQueue    | `io.netty.channel.kqueue`     | macOS/BSD-optimized high performance |
| io_uring  | `io.netty.channel.uring`      | Linux completion-based I/O           |
| OIO       | `io.netty.channel.socket.oio` | Deprecated since 4.1.32              |
| Local     | `io.netty.channel.local`      | In-JVM communication via pipes       |
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
when it finishes). Requires Linux kernel 5.9+. Graduated from incubator
to mainline in Netty 4.2.

**OIO** wraps the classic `java.net` blocking sockets. Deprecated since Netty
4.1.32 (November 2018) — use NIO, Epoll, or KQueue instead.

**Local** enables asynchronous communication between components in the same
JVM through the same Channel API, without touching the network stack.

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
