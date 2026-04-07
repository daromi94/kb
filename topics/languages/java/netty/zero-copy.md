# Zero copy

"Zero-copy" in Netty refers to two distinct layers: kernel-level
transfers that bypass userspace entirely, and application-level
buffer manipulation that avoids memcpy within the JVM. Both compose
— a well-designed server uses OS zero-copy for static file serving
and application zero-copy for protocol processing.

## Two layers

**OS-level zero-copy** moves bytes from a file descriptor to a
socket without copying into userspace. The CPU never touches the
payload; DMA handles the transfer. Netty exposes this through
FileRegion, which maps to `sendfile(2)` on Linux.

**Application-level zero-copy** manipulates ByteBuf instances
without memcpy inside the JVM. Slices, composites, and wrapped
buffers create views and compositions over existing memory. The
payload still lives in userspace and eventually reaches the NIC via
the socket write path, but no redundant copies occur as the message
passes through handlers.

## Gathering writes

The socket write path can flush multiple buffers in a single syscall
via `writev(2)`. When `ctx.write(buf)` is called multiple times
before `flush()`, the ChannelOutboundBuffer accumulates entries and
issues one gathering write.

This is why `write/write/write/flush` outperforms three separate
`writeAndFlush` calls — the latter forces three syscalls and defeats
batching.

CompositeByteBuf and gathering writes are complementary. The
composite gives pipeline handlers a single logical buffer to reason
about. At write time, Netty unwraps the composite into its native
ByteBuffer component array and hands that to `writev`.

## Wrapping external arrays

`Unpooled.wrappedBuffer(byte[])` and
`Unpooled.wrappedBuffer(ByteBuffer)` produce a ByteBuf that reuses
the existing storage without copying. Multi-argument overloads
accept several buffers and return a CompositeByteBuf.

The wrapped array is shared — mutations by the original owner are
visible through the ByteBuf. This is safe for immutable-by-convention
arrays and dangerous for reusable scratch buffers.

## Operations that silently copy

| Operation                             | Zero-copy alternative                |
|---------------------------------------|--------------------------------------|
| `readBytes(length)`                   | `readRetainedSlice(length)`          |
| `copy()`                              | `slice()` or `retainedSlice()`       |
| `writeBytes(otherBuf)` to concatenate | CompositeByteBuf or gathering writes |
| Passing ByteBuf to JDK `byte[]` API   | Redesign to keep hot path in Netty   |
| `toString(charset)` in logger         | Guard with `isDebugEnabled()`        |

Other pitfalls:

- `ByteBuf.array()` on a direct buffer throws. On a heap buffer it
  returns the backing array, which may be larger than capacity —
  downstream code that treats the array as the full contents will
  read stale bytes beyond the writerIndex.
- A transforming outbound handler (compression, chunked encoding)
  between a FileRegion source and the socket kills OS zero-copy
  silently. No error, just degraded performance.

## Measurement

| Signal                      | What it reveals                                               |
|-----------------------------|---------------------------------------------------------------|
| Direct memory churn         | Accidental copies show as allocation churn at req rate        |
| Pooled allocator alloc rate | Copies appear as small/normal allocations at req rate         |
| CPU flame graph             | `writeBytes`, `readBytes`, `copy` are the smoking guns        |
| `strace -c`                 | `sendfile` confirms FileRegion; `read`+`write` means fallback |
| Memory bandwidth (`perf`)   | True zero-copy shows dramatically lower bandwidth             |

## The pipeline principle

Zero-copy is a property of the whole pipeline, not individual
handlers. A single `readBytes` call or a single transforming handler
between source and socket negates careful work elsewhere. Design the
pipeline as a chain of views and compositions, and treat any point
where bytes get memcpy'd as a deliberate choice.

## Related

- [Composite ByteBuf](composite-bytebuf.md) - Application-level buffer composition
- [File region](file-region.md) - OS-level zero-copy via sendfile
- [Derived buffers](derived-buffers.md) - Zero-copy views over ByteBuf
- [ByteBuf](bytebuf.md) - Netty's buffer abstraction

---

Return to [Netty](_index.md)
