# Resource management

Pooled ByteBuf instances are borrowed from a memory pool and must be
explicitly returned. Forgetting to release a buffer leaks native memory
and eventually causes `OutOfMemoryError`. Netty logs a WARN-level
message when it detects leaked resources, but by that point memory is
already being wasted.

## Ownership in channelRead

When a `ChannelInboundHandler` receives a message through `channelRead()`,
the handler owns the buffer. Two valid outcomes:

1. **Pass it downstream** — call `ctx.fireChannelRead(msg)` to transfer
   ownership to the next handler
2. **Consume it** — call `ReferenceCountUtil.release(msg)` to return the
   buffer to the pool

Failing to do either is the most common source of Netty memory leaks.

## SimpleChannelInboundHandler

`SimpleChannelInboundHandler<T>` releases the message automatically after
`channelRead0()` returns. This eliminates manual release bugs but imposes
a constraint: the buffer must not be stored or accessed after the method
exits. Attempting to use a released buffer throws
`IllegalReferenceCountException`.

Use `SimpleChannelInboundHandler` for terminal business logic where the
message is fully consumed in place. Use `ChannelInboundHandler` when the
message must be forwarded or retained beyond the callback.

## Handler comparison

| Aspect    | `ChannelInboundHandler`           | `SimpleChannelInboundHandler`     |
|-----------|-----------------------------------|-----------------------------------|
| Callback  | `channelRead()`                   | `channelRead0()`                  |
| Ownership | Caller owns the message           | Handler releases automatically    |
| Release   | Manual `ReferenceCountUtil`       | Automatic after callback returns  |
| Use case  | Forwarding or retaining a message | Terminal consumption of a message |

## Related

- [ByteBuf](bytebuf.md) - Buffer structure, pooling, and reference counting
- [Channel handler](channel-handler.md) - Handler callbacks and pipeline role
- [Channel pipeline](channel-pipeline.md) - Ordered chain where ownership
  transfers

---

Return to [Netty](_index.md)
