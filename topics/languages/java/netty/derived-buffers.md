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

Decoders extracting a frame from an input buffer should use
`readRetainedSlice(length)`, not `readBytes(length)`. The former
returns a zero-copy view; the latter allocates and copies.

Encoders prepending a header to a payload ByteBuf should combine
them with a CompositeByteBuf, not `writeBytes(payload)` — which
copies the entire payload into the encoding buffer.

## Related

- [Zero copy](zero-copy.md) - Pipeline-wide copy avoidance
- [Composite ByteBuf](composite-bytebuf.md) - Logical buffer composition
- [ByteBuf](bytebuf.md) - Netty's buffer abstraction
- [Resource management](resource-management.md) - Buffer ownership and release

---

Return to [Netty](_index.md)
