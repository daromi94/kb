# Buffer sizing

Buffer sizing works differently on the outbound and inbound sides of
the pipeline. Outbound sizing is deterministic — the application knows
what it is encoding. Inbound sizing is predictive — Netty guesses how
much data the next read will produce.

## Encoder allocation

MessageToByteEncoder calls `allocateBuffer()` before `encode()`. The
default returns `ctx.alloc().ioBuffer()` — a pooled direct buffer with
an initial capacity of 256 bytes. The buffer auto-expands as `encode()`
writes into it, but each expansion triggers a reallocation and memcpy.
For pooled buffers, growth may bump the allocation into a larger size
class, defeating the pool.

Override `allocateBuffer()` when the encoded length is knowable:

```java
@Override
protected ByteBuf allocateBuffer(
        ChannelHandlerContext ctx,
        MyFrame msg,
        boolean preferDirect) {
    int size = HEADER_LEN + msg.payloadLength();

    return preferDirect ? ctx.alloc().ioBuffer(size, size) : ctx.alloc().heapBuffer(size, size);
}
```

Setting initial capacity equal to max capacity prevents any growth.
When only a tight upper bound is available, pass it as the initial
capacity and leave `maxCapacity` at `Integer.MAX_VALUE`.

## Back-patching variable-length fields

When the encoded length depends on what gets written (compression,
nested structures), write a placeholder and patch it afterward:

```java
@Override
protected void encode(
        ChannelHandlerContext ctx,
        MyFrame msg,
        ByteBuf out) {
    int lengthIdx = out.writerIndex();
    out.writeInt(0); // placeholder

    int start = out.writerIndex();
    writePayload(out, msg);

    out.setInt(lengthIdx, out.writerIndex() - start);
}
```

`setXxx()` methods write at an absolute index without advancing
`writerIndex`, which is what back-patching requires.

## Adaptive read-side sizing

On the inbound side, Netty cannot ask application code how large the
next message will be. The default RecvByteBufAllocator for socket
channels is AdaptiveRecvByteBufAllocator, which maintains a predicted
buffer size and adjusts it after each read. The allocator picks sizes
from a precomputed table of increasing values and steps through it:

- **Scale up:** If a read fills the buffer completely, the prediction
  jumps up by 4 index positions in the size table (aggressive ramp-up)
- **Scale down:** If two consecutive reads use only a small fraction
  of the buffer, the prediction drops by 1 position (conservative)

The asymmetry is intentional — under-allocation causes immediate
reallocations, while over-allocation only wastes memory temporarily.
Default bounds clamp predictions to 64 bytes minimum and 64 KiB
maximum.

FixedRecvByteBufAllocator is the alternative when the protocol's
frames are uniform. Set via `ChannelOption.RCVBUF_ALLOCATOR`.

## Sizing rules of thumb

| Scenario              | Strategy                                      |
|-----------------------|-----------------------------------------------|
| Exact size in O(1)    | Override `allocateBuffer()` with exact size   |
| Tight upper bound     | Use upper bound as initial capacity           |
| Variable/unbounded    | Accept 256-byte default, let buffer grow      |
| Length-prefixed frame | Write placeholder, back-patch with `setInt()` |

---

Return to [Netty](_index.md)
