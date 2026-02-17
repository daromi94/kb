# Bootstrap

Bootstrapping is the process of configuring a Netty application's network
layer. A bootstrap object acts as a container for settings that define how
the application interacts with the network — whether it binds to a local
port or connects to a remote peer.

## Bootstrap vs ServerBootstrap

The choice between the two classes depends solely on whether the application
initiates connections or accepts them, regardless of the protocol or data
being processed.

| Aspect          | `Bootstrap` (client)      | `ServerBootstrap` (server)            |
|-----------------|---------------------------|---------------------------------------|
| Network action  | Connects to a remote host | Binds to a local port                 |
| EventLoopGroups | 1                         | 2 (boss + worker)                     |
| Channel type    | `SocketChannel`           | `ServerSocketChannel` + child sockets |

## Boss and worker groups

A server manages two distinct sets of Channels simultaneously:

- **ServerChannel:** A single socket bound to the local port, representing
  the server itself.
- **Accepted Channels:** One socket per connected client, created when a
  connection is accepted.

Netty models this with a parent/child EventLoopGroup pair:

```
         Incoming connections
                 |
                 v
+--------------------------------------+
| Boss group (parent)                  |
| +----------------------------------+ |
| | EventLoop                        | |
| |   accept() -> create child Ch    | |
| +----------------------------------+ |
+--------------------------------------+
                 |
        hand off new Channel
                 |
                 v
+--------------------------------+
| Worker group (child)           |
| +----------+  +----------+     |
| | EventLoop|  | EventLoop| ... |
| |  Ch Ch   |  |  Ch Ch   |     |
| +----------+  +----------+     |
+--------------------------------+
```

**Boss group:** Its EventLoop accepts incoming connection requests and
creates a new Channel for each one.

**Worker group:** Receives the accepted Channel and assigns it an
EventLoop to handle all subsequent I/O and business logic.

Both groups can be the same `EventLoopGroup` instance when resource
sharing is preferred over strict separation.

## Related

- [Event loop](event-loop.md) - EventLoop threading model and Channel
  registration
- [Channel](channel.md) - The I/O conduit created during bootstrapping
- [Netty](netty.md) - Framework overview and core components

---

Return to [Netty](_index.md)
