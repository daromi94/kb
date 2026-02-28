# Thread-per-client

The thread-per-client (or thread-per-connection) model assigns a dedicated
thread to handle the entire lifecycle of a single client connection. It is the
classic concurrency architecture for network servers.

## Workflow

A server following this model uses a strictly synchronous pipeline:

```
+------------------+
| Acceptor thread  |  ServerSocket.accept() blocks in a loop
|       |          |
|  TCP handshake   |  OS completes handshake, accept() returns Socket
|       |          |
|   dispatch       |  new Thread or ThreadPoolExecutor.execute()
|       v          |
+------------------+
| Worker thread    |  Owns the Socket for its full lifetime
|                  |
|  read   (block)  |  Wait for client request data
|  decode          |  Parse protocol (e.g., HTTP)
|  execute         |  Business logic, database queries
|  write  (block)  |  Send response to client
|                  |
|  close / recycle |  Thread terminates or returns to pool
+------------------+
```

The acceptor thread does no processing—it only receives connections and hands
them off. Each worker thread runs a sequential read-decode-execute-write
pipeline, blocking at each I/O boundary.

## Benefits

**Sequential logic:** Code reads as a straight line of instructions. No
callbacks, state machines, or event-driven plumbing. This makes the model
easy to write, test, and debug.

**Thread confinement:** Request data lives in local variables on the worker
thread's private stack. Since no other thread can access these variables,
the data is inherently thread-safe without synchronization.

**Error isolation:** An exception in one worker thread does not affect other
connections. Each request fails independently, simplifying error handling
and recovery.

## Scalability constraints

The model ties one OS thread to each active connection, creating two pressure
points as concurrency grows:

- **Memory:** At the default 1MB stack per thread, 1,000 connections consume
  ~1GB of stack space alone. Scaling to tens of thousands of connections
  (the C10K problem) becomes impractical on 32-bit systems.
- **CPU overhead:** Context switching between thousands of threads consumes
  cycles that would otherwise run application code.

Thread pools (via ExecutorService) bound thread count and queue excess
connections, trading unbounded resource consumption for added latency when
the pool is saturated. Virtual threads (JDK 21) remove the constraint
entirely by multiplexing lightweight threads onto a small carrier pool.

## Related

- [Concurrency models](concurrency-models.md) - Server I/O architecture evolution
- [Blocking I/O](blocking-io.md) - The 1:1 thread-to-request mapping
- [Thread memory](thread-memory.md) - Why local variables are thread-safe
- [Executor service](executor-service.md) - Thread pool abstraction

---

Return to [Concurrency](_index.md)
