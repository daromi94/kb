# Event loop

The EventLoop is Netty's threading primitive. Each EventLoop is backed by
exactly one thread that runs a continuous loop — polling for I/O events,
dispatching them to handlers, and executing submitted tasks. The single-thread
guarantee means all I/O for a given connection is processed sequentially
without synchronization.

## EventLoopGroup

An EventLoopGroup is a pool of EventLoops. It manages their lifecycle and
distributes new Channels among them. A typical server bootstrap creates two
groups: a boss group that accepts connections and a worker group that handles
traffic on accepted channels.

```text
+-------------------------------------------------+
| EventLoopGroup                                  |
| +-----------+  +-----------+  +-----------+     |
| | EventLoop |  | EventLoop |  | EventLoop | ... |
| | (Thread)  |  | (Thread)  |  | (Thread)  |     |
| |  Ch Ch    |  |  Ch Ch    |  |  Ch       |     |
| +-----------+  +-----------+  +-----------+     |
+-------------------------------------------------+
```

## Channel registration

When a new Channel is created, the EventLoopGroup selects an EventLoop and
registers the Channel with it. From that point forward the Channel stays
with the same EventLoop for its entire lifetime.

| Relationship               | Cardinality | Consequence                              |
|----------------------------|-------------|------------------------------------------|
| EventLoopGroup : EventLoop | 1 : N       | Group distributes work across N threads  |
| EventLoop : Thread         | 1 : 1       | All work on that loop is single-threaded |
| EventLoop : Channel        | 1 : N       | One thread multiplexes many connections  |
| Channel : EventLoop        | 1 : 1       | No thread migration, no locking needed   |

Because a Channel never migrates between threads, handler code can safely
use plain fields without `volatile` or `synchronized` — the EventLoop's
single-thread contract provides the memory visibility guarantee.

---

Return to [Netty](_index.md)
