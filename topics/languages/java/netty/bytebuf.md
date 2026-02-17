# ByteBuf

ByteBuf is Netty's replacement for the JDK's `ByteBuffer`. It serves as the
primary container for bytes flowing through the framework and was designed to
fix the usability and performance shortcomings of the standard NIO buffer API.

A companion interface, `ByteBufHolder`, wraps a ByteBuf when additional
metadata needs to travel alongside the payload (e.g. HTTP headers attached to
a body).

## Dual index design

The JDK ByteBuffer uses a single `position` index for both reading and
writing. Switching between modes requires calling `flip()`, which resets the
position — a common source of bugs when forgotten or called twice.

ByteBuf eliminates this by maintaining two independent indices:

```
+-------------------+------------------+------------------+
| discardable bytes |  readable bytes  |  writable bytes  |
+-------------------+------------------+------------------+
0              readerIndex         writerIndex         capacity
```

- **readerIndex** advances on reads, **writerIndex** advances on writes
- No `flip()` call is ever needed
- Bytes between 0 and readerIndex have already been consumed and can be
  discarded to reclaim space

## ByteBuf vs ByteBuffer

| Aspect           | JDK `ByteBuffer`           | Netty `ByteBuf`                  |
|------------------|----------------------------|----------------------------------|
| Index management | Single position index      | Separate reader and writer index |
| Mode switching   | Requires `flip()`          | Automatic                        |
| Capacity         | Fixed, must copy to expand | Dynamic expansion                |
| Zero-copy        | Limited                    | Composite buffer support         |
| Memory reuse     | Not built-in               | Pooling and reference counting   |
| API style        | Imperative                 | Fluent method chaining           |

## Performance features

**Pooling:** Netty maintains pools of ByteBuf instances and reuses them
instead of allocating fresh memory on every I/O operation. This reduces GC
pressure, which is critical for high-throughput servers processing millions
of buffers per second.

**Reference counting:** Each ByteBuf tracks how many consumers hold a
reference to it. When the count drops to zero, the buffer is returned to
the pool (or its memory is freed). This ensures pooled buffers are released
promptly rather than waiting for garbage collection.

**Composite buffers:** A `CompositeByteBuf` presents multiple underlying
buffers as a single logical ByteBuf without copying data between them. This
is Netty's form of zero-copy at the application level — for example,
combining an HTTP header buffer and a body buffer into one message without
a memcpy.

## Related

- [Channel](channel.md) - Reads and writes always go through a ByteBuf
- [Codecs](codecs.md) - Decode ByteBuf into objects and encode back
- [Netty](netty.md) - Framework overview

---

Return to [Netty](_index.md)
