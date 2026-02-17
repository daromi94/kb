# Channel pipeline

A ChannelPipeline is the ordered chain of ChannelHandlers that every Channel
owns. It manages event propagation — both inbound data from the network and
outbound data heading to the socket — and provides the API for installing,
removing, and reordering handlers at runtime.

## Lifecycle

Every new Channel is automatically assigned its own dedicated pipeline. The
setup sequence is:

1. A ChannelInitializer is registered with the ServerBootstrap
2. When `initChannel()` fires, the initializer installs the application's
   handlers into the pipeline
3. The ChannelInitializer removes itself from the pipeline

## Event flow direction

Inbound and outbound events traverse the pipeline in opposite directions:

```
Head                                                  Tail
 |                                                     |
 |  Inbound:  --> [Decoder] --> [Auth] --> [Business]  |
 |  Outbound: <-- [Encoder] <------------- [Business]  |
 |                                                     |
 v                                                     v
Socket                                            Application
```

**Inbound** events flow from head to tail. Each ChannelInboundHandler
processes the data and passes it to the next inbound handler. Processing
ends when data reaches the tail.

**Outbound** events flow from tail to head. When data is written, it passes
through the chain of ChannelOutboundHandlers until it reaches the head,
where the network transport triggers the physical write.

Even when inbound and outbound handlers are interleaved in the same
pipeline, Netty skips handlers of the wrong direction — an inbound event
is only delivered to inbound handlers.

## ChannelHandlerContext

Each handler in the pipeline is wrapped in a ChannelHandlerContext that
represents its binding to the pipeline. The context is the handle used to
forward events to the next handler in the chain.

This context also enables a critical distinction in how outbound writes
are initiated:

| Entry point                     | Starting position | Scope                                |
|---------------------------------|-------------------|--------------------------------------|
| `Channel.write()`               | Tail of pipeline  | Flows through all outbound handlers  |
| `ChannelHandlerContext.write()` | Next handler      | Bypasses preceding outbound handlers |

Writing via the context is useful when a handler knows that earlier
outbound handlers are irrelevant to its message, avoiding unnecessary
processing.

## Adapters

To avoid boilerplate for events a handler does not care about, Netty
provides ChannelInboundHandlerAdapter and ChannelOutboundHandlerAdapter.
These base classes forward every event to the next handler by default,
letting the application override only the methods it needs.

## Related

- [Channel handler](channel-handler.md) - The individual processing units
  in the pipeline
- [Channel handler context](channel-handler-context.md) - Full API and
  advanced usage of the handler-pipeline binding
- [Channel](channel.md) - The connection that owns a pipeline
- [Event loop](event-loop.md) - The thread that drives pipeline execution

---

Return to [Netty](_index.md)
