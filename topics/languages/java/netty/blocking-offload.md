# Blocking offload

Because one EventLoop thread multiplexes many Channels, a blocking call
inside any handler stalls every connection assigned to that thread. Database
queries, synchronous file reads, and legacy API calls are common offenders.
The fix is to run blocking work on a separate thread pool while keeping I/O
handlers on the EventLoop.

## Explicit executor injection

Inject a standard Java Executor or ExecutorService into the handler and
submit blocking work manually. When the work completes, call back into the
pipeline through the ChannelHandlerContext, which is thread-safe and can be
invoked from any thread.

```java
public class SlowDatabaseHandler extends ChannelInboundHandlerAdapter {

    private final Executor executor;

    public SlowDatabaseHandler(Executor executor) {
        this.executor = executor;
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        executor.execute(() -> {
            try {
                Object result = performBlockingQuery(msg);
                ctx.fireChannelRead(result);
            } finally {
                ReferenceCountUtil.release(msg);
            }
        });
    }
}
```

The handler has full control over thread safety, task ordering, and pool
sizing. The application owns the executor lifecycle rather than delegating
it to the pipeline.

## Execution comparison

| Scenario                    | Execution thread     | Tradeoff                                   |
|-----------------------------|----------------------|--------------------------------------------|
| Non-blocking logic          | EventLoop (I/O)      | Highest throughput, minimal switching      |
| Blocking logic on EventLoop | EventLoop (I/O)      | Severe — blocks all connections on thread  |
| Explicit executor offload   | Application executor | Full control, clear ownership of threading |

## Related

- [Event loop](event-loop.md) - I/O engine that must stay unblocked
- [Channel pipeline](channel-pipeline.md) - Where handlers are configured
- [Channel handler context](channel-handler-context.md) - Re-entering the pipeline from other threads

---

Return to [Netty](_index.md)
