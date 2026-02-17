# Channel handler context

A ChannelHandlerContext is created automatically when a handler is added to a
pipeline. It represents the binding between that specific handler and its
position in the chain, and it is the primary handle for forwarding events to
the next handler.

## Propagation scope

The object you invoke a method on determines where event propagation begins:

| Entry point                     | Start position   | Traversal                           |
|---------------------------------|------------------|-------------------------------------|
| `Channel.write()`               | Tail of pipeline | Flows through all outbound handlers |
| `ChannelPipeline.write()`       | Tail of pipeline | Same as Channel                     |
| `ChannelHandlerContext.write()` | Next handler     | Skips all preceding handlers        |

Context-level propagation is the preferred path inside handlers. It avoids
delivering events to handlers that have already processed them or have no
interest, reducing overhead in hot paths.

## API surface

| Category       | Key methods                             | Behavior                                                   |
|----------------|-----------------------------------------|------------------------------------------------------------|
| I/O operations | `write`, `read`, `flush`, `connect`     | Triggers outbound I/O from the next handler                |
| Event triggers | `fireChannelRead`, `fireChannelActive`  | Forwards inbound events to the next inbound handler        |
| Accessors      | `channel()`, `pipeline()`, `executor()` | Returns the associated Channel, Pipeline, or EventExecutor |
| State          | `isRemoved()`                           | True if the handler was removed from the pipeline          |

## Caching and thread safety

A context reference is stable for the lifetime of its handler in the
pipeline. It is safe to store a context in a field and invoke methods on it
later, even from a different thread. This is useful for deferred writes
triggered by external events such as timer callbacks or completed futures.

Calling `pipeline()` on a cached context gives access to dynamic pipeline
manipulation — adding, removing, or replacing handlers at runtime to support
protocol upgrades or feature negotiation.

## @Sharable handlers

A handler instance can be added to multiple pipelines (and thus bound to
multiple contexts) when annotated with `@ChannelHandler.Sharable`.

- The handler must be fully thread-safe
- It must not hold connection-specific state in instance fields
- Typical use: cross-connection metrics or stateless protocol logic
- Adding an unannotated handler to more than one pipeline throws an
  exception

## Related

- [Channel pipeline](channel-pipeline.md) - The ordered chain that owns
  handler contexts
- [Channel handler](channel-handler.md) - The processing unit a context
  wraps
- [Event loop](event-loop.md) - The thread that drives context invocations

---

Return to [Netty](_index.md)
