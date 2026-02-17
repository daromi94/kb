# Blocking offload

Because one EventLoop thread multiplexes many Channels, a blocking call
inside any handler stalls every connection assigned to that thread. Database
queries, synchronous file reads, and legacy API calls are common offenders.
The fix is to run blocking handlers on a separate thread pool while keeping
I/O handlers on the EventLoop.

## EventExecutorGroup

ChannelPipeline's `addLast()` and `addFirst()` accept an optional
`EventExecutorGroup` argument. When provided, Netty dispatches events for
that handler to a thread from the executor group instead of the EventLoop.

```java
EventExecutorGroup blockingGroup = new DefaultEventExecutorGroup(16);

pipeline.addLast(blockingGroup, new SlowDatabaseHandler());
```

DefaultEventExecutorGroup is the standard implementation for non-I/O work.
When the offloaded handler finishes, it uses its ChannelHandlerContext to
pass results back into the pipeline, which re-enters the EventLoop thread
for downstream I/O handlers.

## Execution comparison

| Scenario                    | Execution thread   | Scalability impact                        |
|-----------------------------|--------------------|-------------------------------------------|
| Non-blocking logic          | EventLoop (I/O)    | Highest — minimal context switching       |
| Blocking logic on EventLoop | EventLoop (I/O)    | Severe — blocks all connections on thread |
| Blocking logic on executor  | EventExecutorGroup | Balanced — protects I/O, adds switching   |

## Related

- [Event loop](event-loop.md) - The single-threaded I/O engine that must
  stay unblocked
- [Channel pipeline](channel-pipeline.md) - Where handlers and executor
  groups are configured

---

Return to [Netty](_index.md)
