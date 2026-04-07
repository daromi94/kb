# Partial I/O

In a non-blocking environment, `read()` and `write()` calls do not
guarantee they will process the full amount of data requested. The network
stack prioritizes non-blocking behavior over completing an application-level
request, so applications must handle incomplete transfers explicitly.

## Partial reads

In blocking I/O, requesting 100 bytes suspends the thread until all 100
arrive. In non-blocking I/O, `read()` returns whatever is currently in the
kernel's receive buffer.

A protocol requires a 1,024-byte packet. The client sends it, but due to
network congestion or MTU limits only 400 bytes have arrived at the
server's NIC. The `read()` call returns 400. The application cannot process
the message yet — it must save those 400 bytes in a session-specific buffer,
return to the Selector, and wait for the next read-ready event. When the
remaining 624 bytes arrive, they are appended to the buffer and business
logic can proceed.

## Partial writes

Partial writes occur when the application sends data faster than the
network or receiver can handle it. A 10MB file is written, but the kernel's
fixed-size send buffer is mostly full and only accepts 64KB. The `write()`
returns 65,536. The application is responsible for the remaining bytes. It
cannot simply loop and call `write()` again immediately — that would likely
return EAGAIN and waste CPU. Instead, the socket must be registered for an
`OP_WRITE` event so the OS signals when send buffer space is available.

| Aspect          | Partial read                             | Partial write                                 |
|-----------------|------------------------------------------|-----------------------------------------------|
| Cause           | Data has not arrived over the wire yet   | OS outgoing buffer is full or congested       |
| Symptom         | `read()` returns less than expected size | `write()` returns less than total buffer size |
| Action required | Store in local buffer, wait for more     | Store remaining data, wait for write-ready    |

## Netty's solutions

### ByteToMessageDecoder (reads)

Netty provides frame decoders that define message boundaries — for example
"every message ends with `\n`" or "the first 4 bytes indicate the length."
Netty's internal ByteBuf accumulates partial reads automatically. Only when
a complete frame is assembled does it pass the data to the next
ChannelHandler in the pipeline.

### Channel write queue (writes)

When application code calls `ctx.write(msg)`, Netty does not necessarily
invoke the OS `write()` immediately:

1. The message is placed into an internal write buffer queue
2. Netty attempts to flush the queue to the socket
3. If the OS accepts only a partial write, Netty tracks the remaining
   bytes and handles `OP_WRITE` registration automatically

Application code sees a ChannelFuture that completes once the entire
message has been sent, hiding the partial-write machinery entirely.

## Related

- [Non-blocking sockets](non-blocking-sockets.md) - Why partial I/O occurs
- [Netty](netty.md) - Framework that abstracts partial I/O handling
- [Selector](selector.md) - The multiplexer driving read/write-ready
  notifications

---

Return to [Netty](_index.md)
