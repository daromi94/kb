# Netty

Asynchronous, event-driven network application framework for Java.

## Notes

- [Netty](netty.md) - Architecture and design rationale
- [BIO scaling walls](bio-scaling-walls.md) - Thread-per-connection bottlenecks
- [Non-blocking sockets](non-blocking-sockets.md) - Non-blocking socket mechanics
- [Selector](selector.md) - I/O readiness multiplexing
- [Partial I/O](partial-io.md) - Incomplete reads and writes
- [Event loop](event-loop.md) - Threading and I/O dispatch
- [Channel](channel.md) - Bidirectional I/O conduit
- [Channel future](channel-future.md) - Listener-based async tracking
- [ByteBuf](bytebuf.md) - Netty's buffer abstraction
- [ByteBuf allocators](bytebuf-allocators.md) - Arena-based memory pooling
- [Buffer sizing](buffer-sizing.md) - Encoder and Decoder allocations
- [Derived buffers](derived-buffers.md) - Zero-copy views over ByteBuf
- [Resource management](resource-management.md) - Buffer ownership and release
- [Leak detection](leak-detection.md) - Unreleased buffer diagnostics
- [Channel handler](channel-handler.md) - Pipeline event processing units
- [Channel pipeline](channel-pipeline.md) - Handler chain and event flow
- [Channel handler context](channel-handler-context.md) - Handler-pipeline binding
- [Exception handling](exception-handling.md) - Error propagation paths
- [Blocking offload](blocking-offload.md) - Threading out blocking work
- [Codecs](codecs.md) - Byte-object encoder/decoder handlers
- [Transport](transport.md) - Pluggable I/O mechanisms
- [Bootstrap](bootstrap.md) - Client and server wiring

---

Return to [Java](../_index.md)
