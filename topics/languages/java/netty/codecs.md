# Codecs

Encoders and decoders — collectively codecs — are specialized
ChannelHandlers that translate between raw network bytes and the Java
objects an application works with.

## Direction

| Component | Conversion       | Direction |
|-----------|------------------|-----------|
| Decoder   | Bytes -> Message | Inbound   |
| Encoder   | Message -> Bytes | Outbound  |

## Base classes

Netty provides abstract base classes whose names reflect the conversion
they perform:

**ByteToMessageDecoder** handles inbound data. It overrides `channelRead`,
calls a `decode()` method that subclasses implement, and forwards the
resulting object to the next ChannelInboundHandler in the pipeline.

**MessageToByteEncoder** handles outbound data. It converts a message to
bytes and forwards them to the next ChannelOutboundHandler.

Netty also ships pre-built codecs for common protocols — ProtobufEncoder,
ProtobufDecoder, HttpObjectDecoder, and others — so standard wire formats
rarely need custom codec work.

## SimpleChannelInboundHandler

Once a decoder has produced a typed Java object, the application needs a
handler for business logic. SimpleChannelInboundHandler fills this
role:

- **Type safety:** The generic parameter `T` restricts the handler to a
  single message type
- **`channelRead0(ctx, msg)`:** The method to override — receives the
  decoded message and the ChannelHandlerContext
- **Automatic release:** After `channelRead0` returns, the handler
  releases the message's reference count, preventing memory leaks

As with all handlers, `channelRead0` must not block the EventLoop thread.

## Related

- [Channel handler](channel-handler.md) - The handler abstraction codecs
  build on
- [Channel pipeline](channel-pipeline.md) - Where codecs are installed in
  the processing chain

---

Return to [Netty](_index.md)
