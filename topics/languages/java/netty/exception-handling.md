# Exception handling

Netty splits exception handling into two paths matching its inbound/outbound
event model. Inbound exceptions propagate through the pipeline like data.
Outbound exceptions surface asynchronously through futures and promises.

## Inbound exceptions

An inbound exception — a decoder failure, an unexpected disconnect — flows
head-to-tail through the pipeline, the same direction as data. Each handler
gets a chance to handle it via `exceptionCaught(ChannelHandlerContext,
Throwable)`.

A common pattern is a catch-all handler at the tail of the pipeline. Because
exceptions propagate forward, placing the handler last ensures nothing slips
through unhandled. If no handler consumes the exception, Netty logs it and
drops it.

## Outbound exceptions

Outbound operations (`write()`, `connect()`) return immediately. Failures
surface later through two mechanisms:

**ChannelFutureListener** — attach a listener to the returned ChannelFuture.
The listener fires once the operation completes, whether it succeeded or
failed. Best for call-site-specific reactions like closing on write failure.

**ChannelPromise** — outbound handler methods receive a ChannelPromise
argument. The handler calls `setSuccess()` or `setFailure(Throwable)` to
signal the outcome. Adding a listener to this promise inside the handler
provides generic error logic that applies to all operations passing through
that handler.

If a ChannelOutboundHandler itself throws during processing, Netty
automatically notifies listeners on the corresponding ChannelPromise.

## Summary

| Path     | Mechanism          | Pattern                                           |
|----------|--------------------|---------------------------------------------------|
| Inbound  | Event propagation  | Override `exceptionCaught()` at pipeline tail     |
| Outbound | Future listener    | `future.addListener()` at the call site           |
| Outbound | Promise completion | `promise.setFailure()` inside an outbound handler |

## Related

- [Channel handler](channel-handler.md) - The `exceptionCaught` callback
- [Channel future](channel-future.md) - Completion notification via listeners
- [Channel pipeline](channel-pipeline.md) - The chain exceptions traverse

---

Return to [Netty](_index.md)
