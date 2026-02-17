# Channel handler

A ChannelHandler is a modular component that reacts to I/O events — data
received, connection established, error occurred — as data flows through a
Channel. Instead of one monolithic function for all networking logic, Netty
breaks processing into small, reusable handlers chained together in a
pipeline.

## Inbound and outbound

Handlers are split by data direction:

**ChannelInboundHandler** processes data arriving from the remote peer:
decoding bytes into Java objects, applying business logic, handling state
changes like `channelActive` or `channelRead`.

**ChannelOutboundHandler** processes data leaving the application: encoding
Java objects into bytes, managing connection requests (`connect`,
`disconnect`), flushing data to the socket.

## Lifecycle callbacks

Handlers are collections of callbacks invoked by Netty when events occur:

| Callback               | Trigger                                 |
|------------------------|-----------------------------------------|
| `channelRead()`        | Data read from the Channel              |
| `channelActive()`      | Channel connected and ready for I/O     |
| `exceptionCaught()`    | Error during an I/O operation           |
| `write()`              | Application requests to send data       |
| `userEventTriggered()` | Custom event (e.g., idle state timeout) |

## Pipeline

A ChannelPipeline is an ordered chain of handlers that data traverses
sequentially. Each handler performs one step and passes the result to the
next:

```
Inbound:  bytes --> [Decoder] --> [Auth] --> [Business logic]
Outbound: bytes <-- [Encoder] <------------- [Business logic]
```

For a login request, the decoder converts raw bytes into a LoginRequest
object, the auth handler validates credentials, and the encoder converts
the LoginResponse back to bytes. Each handler is reusable — a standard
SSL handler or HTTP decoder can be dropped into any pipeline without
changing business logic.

## Never block the EventLoop

A ChannelHandler executes on the EventLoop thread, which may be managing
thousands of connections. Blocking inside a handler (long database query,
`Thread.sleep()`) freezes all those connections. Heavy work must be
offloaded to a separate thread pool.

## Related

- [Channel pipeline](channel-pipeline.md) - The ordered chain that
  handlers plug into
- [Channel](channel.md) - The connection that handlers process
- [Channel future](channel-future.md) - Tracking async results from
  handler operations
- [Netty](netty.md) - Framework overview and core components

---

Return to [Netty](_index.md)
