# Channel

A Channel is the fundamental abstraction for any I/O operation in Java
NIO and Netty. It represents an open connection to a network socket or
I/O component capable of reading and writing. Where traditional I/O uses
unidirectional streams (one InputStream, one OutputStream), a Channel is
a bidirectional conduit through which data flows in both directions.

## Key properties

**State-based:** A Channel follows a defined lifecycle with four states.
State transitions fire events through the ChannelPipeline to inbound
handlers.

**Non-blocking capable:** A Channel can be configured in non-blocking mode,
allowing read and write operations to return immediately even when no data
is ready, rather than suspending the thread.

**Buffer-oriented:** Channels never move data directly. They always
interact with a Buffer (ByteBuf in Netty). You ask the Channel to read
bytes into a buffer or write a buffer's contents to the underlying entity.

## Lifecycle states

A Channel progresses through these states in order:

```text
Unregistered --> Registered --> Active --> Inactive --> Unregistered
```

| State                 | Meaning                                   | Handler callback        |
|-----------------------|-------------------------------------------|-------------------------|
| `ChannelUnregistered` | Created but not yet bound to an EventLoop | `channelUnregistered()` |
| `ChannelRegistered`   | Bound to an EventLoop                     | `channelRegistered()`   |
| `ChannelActive`       | Connected to remote peer, ready for I/O   | `channelActive()`       |
| `ChannelInactive`     | Disconnected from remote peer             | `channelInactive()`     |

Common patterns: send a greeting message in `channelActive()`, release
resources in `channelInactive()`.

## Channel types

| Channel type        | Entity               | Use case                                    |
|---------------------|----------------------|---------------------------------------------|
| FileChannel         | File on local disk   | High-speed file transfers, memory mapping   |
| SocketChannel       | TCP socket (client)  | Connecting to a server, exchanging data     |
| ServerSocketChannel | TCP listening socket | Accepting incoming connections              |
| DatagramChannel     | UDP socket           | Connectionless packet exchange (DNS, video) |

## Channel vs stream

| Aspect    | Stream (java.io)               | Channel (java.nio)                    |
|-----------|--------------------------------|---------------------------------------|
| Direction | Unidirectional (in or out)     | Bidirectional (read and write)        |
| Blocking  | Always blocks on read/write    | Configurable non-blocking mode        |
| Data unit | Byte-by-byte                   | Buffer-oriented (block of data)       |
| Scaling   | One stream pair per connection | Registers with Selector for thousands |

## Netty's Channel

A Java NIO SocketChannel is a low-level OS wrapper. A Netty Channel is a
richer object that integrates with the framework:

- Bound to a single EventLoop for its entire lifetime, ensuring all I/O
  is handled sequentially and thread-safely
- Connected to a ChannelPipeline that processes inbound and outbound data
  through a chain of handlers
- Provides ChannelFuture for asynchronous operation tracking

## Related

- [Channel handler](channel-handler.md) - Logic that processes data
  flowing through a Channel
- [Channel future](channel-future.md) - Tracking asynchronous Channel
  operations
- [Netty](netty.md) - Framework overview and core components

---

Return to [Netty](_index.md)
