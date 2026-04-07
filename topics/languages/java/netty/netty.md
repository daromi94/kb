# Netty

Netty is an asynchronous, event-driven network application framework for
Java. It simplifies high-performance protocol server and client development
by abstracting the low-level details of Java NIO. Netty powers the
networking layers of Cassandra, Elasticsearch, gRPC, and Minecraft.

## Design goals

**Complexity shielding:** Hides NIO boilerplate and known JDK bugs such as
the infamous epoll 100% CPU spin where the Selector enters a busy-wait loop
even when no I/O events are pending. Netty detects and works around this
automatically.

**Performance:** Provides better throughput and lower latency than standard
Java libraries through pooled buffer management and optimized resource
usage.

**Flexibility:** Supports HTTP, HTTP/2, WebSockets, Protobuf, SSL/TLS out
of the box while allowing custom protocol implementations.

## Core components

### Channel

Represents an open connection to a network socket or I/O component
capable of operations such as reading, writing, connecting, and binding.

### EventLoop

A single thread running a continuous loop that monitors I/O events (data
received, connection accepted) and dispatches them to handlers. Each
Channel is bound to one EventLoop for its entire lifetime, guaranteeing
that all I/O for that connection is sequential and thread-safe without
explicit synchronization.

### ChannelHandler and ChannelPipeline

When an event occurs, it flows through a ChannelPipeline — a chain of
ChannelHandlers that each perform a discrete processing step:

```text
Inbound                                             Outbound
+----------------+  +-----------------+  +-------+  +-----------------+  +----------------+
| Decoder        |->| Decoder         |->| Biz   |->| Encoder         |->| Encoder        |
| (bytes->frame) |  | (frame->object) |  | logic |  | (object->frame) |  | (frame->bytes) |
+----------------+  +-----------------+  +-------+  +-----------------+  +----------------+
```

- **Decoder handlers** transform raw bytes into Java objects
- **Business logic handlers** process objects and decide responses
- **Encoder handlers** transform Java objects back into bytes

## Why Netty over raw NIO

| Feature          | Raw Java NIO                      | Netty                                  |
|------------------|-----------------------------------|----------------------------------------|
| API              | Low-level, verbose                | High-level, fluent, modular            |
| Buffer mgmt      | Manual ByteBuffer flip/track      | Pooled ByteBuf with reference counting |
| Protocol support | Build encoders/decoders yourself  | Built-in HTTP, SSL, WebSockets, etc.   |
| Thread model     | Manual selector and thread safety | Reactor-based EventLoop model          |
| Zero-copy        | Limited support                   | Extensive support via CompositeByteBuf |
| Known bugs       | Epoll spin bug is your problem    | Detected and worked around internally  |

## Related

- [BIO scaling walls](bio-scaling-walls.md) - Problem Netty was built to solve
- [Non-blocking sockets](non-blocking-sockets.md) - OS-level mechanics Netty abstracts
- [Selector](selector.md) - The multiplexer at the heart of NIO
- [Channel](channel.md) - The bidirectional I/O conduit
- [Channel handler](channel-handler.md) - Modular event processing
- [Channel future](channel-future.md) - Listener-based async tracking
- [Partial I/O](partial-io.md) - Handling incomplete reads and writes

---

Return to [Netty](_index.md)
