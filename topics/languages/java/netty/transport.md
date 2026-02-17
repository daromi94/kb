# Transport

A transport is the mechanism Netty uses to move data across the network (or
within a JVM). In standard Java, blocking and non-blocking I/O have completely
different APIs — switching from `java.net` to `java.nio` typically requires a
full rewrite. Netty solves this by layering a single API over all transport
implementations, so application code always works with Channel,
ChannelPipeline, and ChannelHandler regardless of the underlying I/O model.

## Switching transports

Because the transport is an implementation detail hidden behind Netty's
abstractions, migrating from blocking to non-blocking I/O reduces to changing
two classes in the bootstrap configuration:

```java
// Blocking (OIO)
bootstrap.group(new OioEventLoopGroup()).channel(OioServerSocketChannel.class)

// Non-blocking (NIO)
bootstrap.group(new NioEventLoopGroup()).channel(NioServerSocketChannel.class)
```

The rest of the application — handlers, pipeline, business logic — remains
untouched. This is in sharp contrast to raw JDK code, where the OIO and NIO
versions of the same program share almost no structure.

## Available transports

| Transport | Package                       | Use case                           |
|-----------|-------------------------------|------------------------------------|
| NIO       | `io.netty.channel.socket.nio` | High-concurrency, scalable servers |
| Epoll     | `io.netty.channel.epoll`      | Linux-optimized high performance   |
| OIO       | `io.netty.channel.socket.oio` | Small-to-moderate concurrency      |
| Local     | `io.netty.channel.local`      | In-JVM communication via pipes     |
| Embedded  | `io.netty.channel.embedded`   | Unit testing ChannelHandlers       |

**NIO** is the default choice for production. It uses I/O multiplexing via a
Selector, allowing a small number of threads to manage thousands of
connections.

**Epoll** uses JNI to call Linux's `epoll()` directly, bypassing the JDK's
NIO layer. It is faster than the NIO transport, fully non-blocking, and
exposes Linux-specific socket options like `SO_REUSEPORT`. Linux-only.

**OIO** wraps the classic `java.net` blocking sockets. Useful when integrating
with libraries that require blocking semantics, but limited in scalability.

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
