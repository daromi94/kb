# Derived buffers

Derived buffers are zero-copy views over an existing ByteBuf. They
share the same backing memory but maintain independent indices, so
creation is O(1) with no memcpy.

## How they work

A ByteBuf has two parts: metadata (readerIndex, writerIndex, capacity)
and physical storage (the `byte[]` or native memory). Derived buffer
methods create a new metadata object pointing at the same storage.
Indices diverge independently, but writes through either view mutate
the shared memory.

## View methods

| Method         | View scope                  | Indices                            |
|----------------|-----------------------------|------------------------------------|
| `duplicate()`  | Full buffer (same capacity) | Copies parent's reader/writer      |
| `slice()`      | Readable region only        | readerIndex = 0, writerIndex = len |
| `asReadOnly()` | Same as parent              | Read-only; writes throw            |

`slice()` maps its internal index 0 to the parent's `readerIndex`,
so only the readable portion is visible. `duplicate()` exposes the
entire buffer.

## Reference counting

Derived buffers share the parent's reference count. `slice()` and
`duplicate()` do **not** call `retain()`. If the parent is released,
accessing the derived buffer throws IllegalReferenceCountException.

When a derived buffer must outlive its parent, use the retained
variants:

| Method                | Equivalent to          |
|-----------------------|------------------------|
| `retainedSlice()`     | `slice().retain()`     |
| `retainedDuplicate()` | `duplicate().retain()` |

These increment the reference count at creation, keeping the backing
memory alive until the derived buffer is also released.

## Decoder and encoder patterns

In decoders, prefer `readRetainedSlice(length)` over
`readBytes(length)` when carving frames from a cumulation buffer.
`readRetainedSlice` creates a zero-copy view with a reference count
bump. `readBytes` allocates fresh memory and copies the bytes — at
high throughput, this difference translates to gigabytes per second
of wasted memory bandwidth.

In encoders, avoid `writeBytes(payload)` when combining a header
with a payload ByteBuf the caller provided. `writeBytes` between
two ByteBuf instances is a memcpy. Emit the header separately and
use a CompositeByteBuf to combine them without copying.

## Related

- [Zero copy](zero-copy.md) - Pipeline-wide copy avoidance
- [Composite ByteBuf](composite-bytebuf.md) - Logical buffer composition
- [ByteBuf](bytebuf.md) - Netty's buffer abstraction
- [Resource management](resource-management.md) - Buffer ownership and release

---

Return to [Netty](_index.md)
