# Non-blocking sockets

In a blocking socket, calling `read()` suspends the thread until data
arrives or the connection times out. Non-blocking sockets invert this by
configuring the OS to return immediately when no data is available, shifting
responsibility for tracking readiness to the application.

## The O_NONBLOCK flag

A socket is made non-blocking via the `fcntl` (file control) system call:

```c
int flags = fcntl(socket_fd, F_GETFL, 0);
fcntl(socket_fd, F_SETFL, flags | O_NONBLOCK);
```

Once set, `read()` and `write()` no longer suspend the calling thread.
The kernel checks the socket's internal buffer and returns immediately
with whatever is available — or an error code if nothing is.

## EAGAIN and EWOULDBLOCK

When a non-blocking operation cannot complete, the system returns `-1` and
sets `errno` to one of two values:

- **EAGAIN:** "Try again." The resource is temporarily unavailable.
- **EWOULDBLOCK:** "The operation would block."

On modern Linux these are defined as the same value. Receiving either is
not a failure — it signals that no data is available right now. Application
code must check for these explicitly and retry later.

## Read and write behavior

| Operation  | Blocking socket                     | Non-blocking socket                   |
|------------|-------------------------------------|---------------------------------------|
| `read()`   | Thread sleeps until data available  | Returns data or EAGAIN immediately    |
| `write()`  | Thread sleeps if buffer full        | Writes what it can, EAGAIN if full    |
| CPU impact | High overhead for many idle threads | High overhead if busy-polling in loop |
| Best with  | Low-concurrency, simple clients     | High-concurrency, I/O multiplexing    |

## The state machine requirement

Because `read()` and `write()` can return partial results or "try again"
signals, application logic can no longer follow a simple linear flow. The
application must maintain a state machine:

**Partial reads:** A protocol header requires 100 bytes but `read()`
returns only 40. Those 40 bytes must be stored in a session buffer. The
application returns to the event loop and waits for the next read-ready
notification to collect the remaining 60.

**Partial writes:** When the OS send buffer is full, `write()` may only
transmit half the data. The application must track the unsent bytes and
register for a write-ready event to send the rest later.

This complexity — managing buffers, tracking offsets, handling partial
results — is the fundamental reason Netty exists as an abstraction layer.

## Why selectors are required

Running a loop that constantly calls `read()` on a non-blocking socket is
busy-waiting. It spikes CPU usage to 100% because the thread never yields.
Non-blocking sockets must be paired with an I/O multiplexer (like `epoll`
or Java's Selector) that blocks on behalf of all registered sockets and
wakes the application only when a socket is genuinely ready.

---

Return to [Netty](_index.md)
