# Asynchronous I/O

Asynchronous I/O is a programming model that allows a single thread to handle
multiple operations without blocking while waiting for them to finish.

## Characteristics

**Non-blocking:** When the thread initiates an I/O task (like a database
query), it does not wait for the response. It sends the request and immediately
becomes available to handle other tasks.

**Single-threaded efficiency:** Commonly associated with environments like
Node.js, which uses a single thread to manage many concurrent operations
efficiently.

**Callbacks and promises:** Results are handled once the task finishes using
callback functions. Modern code uses Promises and async/await syntax for
readability.

## Best use case

Highly effective for **I/O-bound tasks** (network requests, file reading)
because it prevents the CPU from sitting idle while waiting for slow external
resources.

## Related

- [Synchronous I/O](synchronous-io.md) - The blocking alternative
- [Async I/O vs multithreading](async-vs-multithreading.md) - Comparison of
  approaches
