# Channel future

In Netty, every I/O operation — `connect()`, `write()`, `close()` — returns
immediately before it completes. A ChannelFuture is the object that tracks
the operation's progress and notifies the application when it finishes.

A ChannelFuture acts as a placeholder for the result of an operation
that will be executed in the future. ChannelFuture extends Java's
`Future` with a listener-based callback mechanism that avoids blocking.

## Java Future limitations

Java's `java.util.concurrent.Future` provides `get()` to retrieve a
result, but the call blocks the thread until the task completes. There
is no way to say "call this method when the result is ready" — the only
alternatives are blocking with `get()` or polling with `isDone()`. Futures
also lack chaining (run task B after task A) and ergonomic error handling.

These limitations make standard Futures unsuitable for Netty, where
blocking the EventLoop thread would freeze thousands of connections.

## The listener pattern

Since blocking on `get()` is not an option, Netty provides a
callback-style notification system. A ChannelFuture allows registering
a ChannelFutureListener. The EventLoop invokes the listener once the
operation completes, regardless of whether it succeeded or failed:

1. **Initiate:** `cf = channel.writeAndFlush(data)` returns immediately
2. **Attach:** `cf.addListener(myListener)` registers a callback
3. **Continue:** The calling thread is free for other work
4. **Notify:** Once the write and flush completes, Netty triggers
   `myListener.operationComplete(cf)`

## Completion states

When a ChannelFuture is returned, the operation may be in any state:

- **Uncompleted** — still in progress
- **Completed successfully** — operation finished normally
- **Failed** — an error occurred (retrieve via `cause()`)
- **Cancelled** — aborted by the application

## Key methods

| Method          | Behavior                                          |
|-----------------|---------------------------------------------------|
| `addListener()` | Register callback for completion (preferred)      |
| `channel()`     | Returns the associated Channel                    |
| `isSuccess()`   | Whether the operation completed successfully      |
| `cause()`       | The Throwable if the operation failed             |
| `sync()`        | Blocks until complete, rethrows failures on error |
| `await()`       | Blocks until complete, does not rethrow           |

## Never block in handlers

`sync()` and `await()` exist for setup code (e.g., Bootstrap
configuration) but must never be called inside a ChannelHandler. The
handler runs on the EventLoop. Calling `sync()` tells the EventLoop to
wait for the I/O operation to finish — but the EventLoop is the very
thread that would complete it, so it deadlocks.

## Write-then-close pattern

A common pattern is sending a final message and closing the connection.
Without futures, `close()` may execute before `write()` finishes:

```java
// Wrong: close() may race ahead of write()
channel.writeAndFlush(msg);
channel.close();

// Right: close only after write completes
ChannelFuture f = channel.writeAndFlush(msg);
f.addListener(ChannelFutureListener.CLOSE);
```

`ChannelFutureListener.CLOSE` is a built-in listener that closes the
Channel unconditionally when the future completes, regardless of whether
the operation succeeded or failed.

## Related

- [Channel](channel.md) - The connection whose operations produce futures
- [Channel handler](channel-handler.md) - Where listener-based futures
  replace blocking calls
- [Netty](netty.md) - Framework overview and core components

---

Return to [Netty](_index.md)
