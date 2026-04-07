# Composite ByteBuf

CompositeByteBuf presents multiple backing buffers as a single
logical ByteBuf — readable, writable, with correct index arithmetic
across component boundaries — without copying any of them. It is
the workhorse of application-level zero-copy in Netty.

## Protocol framing

The canonical use case is prepending a header to a body. A handler
produces a 12-byte header and needs to combine it with a 50 KiB
body from upstream. The naive approach allocates a new buffer and
copies both pieces. The composite approach:

```java
@Override
protected void encode(ChannelHandlerContext ctx, Msg msg, List<Object> out) {
    ByteBuf header = ctx.alloc().directBuffer(12);
    header.writeInt(msg.type()).writeLong(msg.bodySize());

    CompositeByteBuf framed = ctx.alloc().compositeBuffer(2);
    framed.addComponents(true, header, msg.body());
    out.add(framed);
}
```

Two wrapper allocations, zero memcpy.

## Message aggregation

Composites shine when assembling a message across multiple reads.
An HTTP/1.1 chunked body arriving in seven TCP reads can be
aggregated by calling `addComponent(true, chunk)` seven times. The
result is a single logical ByteBuf with no intermediate copies.

## The writerIndex flag

The boolean parameter in `addComponent(true, buf)` advances the
composite's writerIndex by the component's readable bytes. Without
it, components are added but the writerIndex stays at 0 — the
composite appears empty to downstream readers.

This is a common source of bugs. Always pass `true` unless there is
a specific reason to manage the writerIndex manually.

## Access performance

Every `getByte(i)` call binary-searches the component array to find
which component contains index `i`. For handlers that iterate
byte-by-byte, this overhead matters. For handlers that slice out
sub-regions and pass them downstream, it does not — a slice that
falls within a single component delegates directly to that
component's storage.

If a composite accumulates many tiny buffers and the read path does
per-byte iteration, profile the application. Beyond 16-32 components
it may be faster to consolidate (copy) into a single buffer once
than to pay the per-access search cost repeatedly.

## Release semantics

Adding a component to a CompositeByteBuf transfers ownership.
Releasing the composite releases each component exactly once. Do not
manually release buffers after adding them — double-release throws
IllegalReferenceCountException.

## Related

- [Zero copy](zero-copy.md) - Gathering writes and the pipeline principle
- [ByteBuf](bytebuf.md) - Netty's buffer abstraction
- [Derived buffers](derived-buffers.md) - Zero-copy views over ByteBuf
- [Resource management](resource-management.md) - Buffer ownership and release

---

Return to [Netty](_index.md)
