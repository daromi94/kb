# Netty

Asynchronous, event-driven network application framework for Java.

## Notes

- [Netty](netty.md) - Event-driven networking framework built on Java NIO
- [BIO scaling walls](bio-scaling-walls.md) - Thread-per-connection bottlenecks Netty overcomes
- [Non-blocking sockets](non-blocking-sockets.md) - OS-level socket mechanics that Netty abstracts
- [Selector](selector.md) - I/O multiplexer at the heart of NIO
- [Event loop](event-loop.md) - Single-threaded I/O engine and thread model
- [Channel](channel.md) - Bidirectional I/O conduit abstraction
- [ByteBuf](bytebuf.md) - Pooled buffer replacing JDK ByteBuffer
- [Channel handler](channel-handler.md) - Modular event processing in the pipeline
- [Resource management](resource-management.md) - ByteBuf ownership and release in handlers
- [Channel pipeline](channel-pipeline.md) - Ordered handler chain and event propagation
- [Codecs](codecs.md) - Encoder/decoder handlers for byte-object translation
- [Bootstrap](bootstrap.md) - Configuring client and server network layers
- [Transport](transport.md) - Unified API over pluggable I/O mechanisms
- [Channel future](channel-future.md) - Listener-based async operation tracking
- [Partial I/O](partial-io.md) - Handling incomplete reads and writes in non-blocking I/O

---

Return to [Java](../_index.md)
