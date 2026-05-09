# Zero copy

"Zero-copy" in Netty means two different things.

**OS-level zero-copy** moves bytes from a file descriptor to a
socket without copying into userspace. The CPU never touches the
payload; DMA handles the transfer. Netty exposes this through
FileRegion, which maps to `sendfile(2)` on Linux.

**Application-level zero-copy** manipulates ByteBuf instances
without memcpy inside the JVM. Slices, composites, and wrapped
buffers create views over existing memory rather than allocating
and copying into new buffers at each pipeline stage.

## Gathering writes

The socket write path can flush multiple buffers in a single syscall
via `writev(2)`. When `ctx.write(buf)` is called multiple times
before `flush()`, the ChannelOutboundBuffer accumulates entries and
issues one gathering write.

This is why `write/write/write/flush` outperforms three separate
`writeAndFlush` calls — the latter forces three syscalls and defeats
batching.

At write time, Netty unwraps a CompositeByteBuf into its native
ByteBuffer component array and hands that to `writev`, combining
logical composition with syscall-level batching.

## Wrapping existing memory

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

---

Return to [Netty](_index.md)
