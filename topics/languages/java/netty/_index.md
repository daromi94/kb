# Netty

Asynchronous, event-driven network application framework for Java.

## Notes

- [Netty](netty.md) - Event-driven networking framework built on Java NIO
- [BIO scaling walls](bio-scaling-walls.md) - Thread-per-connection bottlenecks Netty overcomes
- [Non-blocking sockets](non-blocking-sockets.md) - OS-level socket mechanics that Netty abstracts
- [Selector](selector.md) - I/O multiplexer at the heart of NIO
- [Partial I/O](partial-io.md) - Handling incomplete reads and writes in non-blocking I/O
- [Event loop](event-loop.md) - Single-threaded I/O engine and thread model
- [Channel](channel.md) - Bidirectional I/O conduit abstraction
- [Channel future](channel-future.md) - Listener-based async operation tracking
- [ByteBuf](bytebuf.md) - Pooled buffer replacing JDK ByteBuffer
- [Resource management](resource-management.md) - ByteBuf ownership and release in handlers
- [Leak detection](leak-detection.md) - Diagnosing unreleased buffers with ResourceLeakDetector
- [Channel handler](channel-handler.md) - Modular event processing in the pipeline
- [Channel pipeline](channel-pipeline.md) - Ordered handler chain and event propagation
- [Channel handler context](channel-handler-context.md) - Handler-pipeline binding and scoped event propagation
- [Exception handling](exception-handling.md) - Inbound propagation and outbound future/promise errors
- [Blocking offload](blocking-offload.md) - Explicit executor offload for blocking work
- [Codecs](codecs.md) - Encoder/decoder handlers for byte-object translation
- [Transport](transport.md) - Unified API over pluggable I/O mechanisms
- [Bootstrap](bootstrap.md) - Configuring client and server network layers

---

Return to [Java](../_index.md)
