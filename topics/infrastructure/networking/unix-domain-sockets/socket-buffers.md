# Socket buffers

The kernel maintains a **send queue** (TX) and **receive queue** (RX) for each
side of a UDS connection. These kernel-space buffers decouple producers from
consumers, allowing asynchronous data exchange between processes.

## Queue Architecture

```text
  Process A                  Kernel                 Process B
+-----------+    write()   +--------+   internal   +--------+    read()   +-----------+
| Userspace | -----------> | Send Q | -----------> | Recv Q | ----------> | Userspace |
| buffer    |  user->kern  |  (TX)  |  kern->kern  |  (RX)  |  kern->user | buffer    |
+-----------+              +--------+              +--------+             +-----------+
```

A `write()` copies data from userspace into the local send queue. The kernel
moves it to the peer's receive queue. A `read()` copies data out to the
reader's userspace buffer. Two copies total — user-to-kernel and
kernel-to-user — but no network stack processing.

## Buffer Sizing

Queue sizes are governed by system defaults and per-socket overrides:

| Sysctl                  | Controls          |
|-------------------------|-------------------|
| `net.core.wmem_default` | Default send size |
| `net.core.rmem_default` | Default recv size |

Per-socket tuning via `setsockopt`:

```c
int size = 262144; // 256 KB
setsockopt(fd, SOL_SOCKET, SO_SNDBUF, &size, sizeof(size));
setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size));
```

## Blocking vs Non-Blocking

Queue fullness determines whether I/O calls block or return immediately:

| Condition        | Blocking socket          | Non-blocking socket   |
|------------------|--------------------------|-----------------------|
| Send queue full  | Thread sleeps until room | Returns `EAGAIN`      |
| Recv queue empty | Thread sleeps until data | Returns `EWOULDBLOCK` |

Non-blocking sockets pair with `epoll`, `select`, or `poll` to retry when
the kernel signals readiness.

## Kernel Synchronization

When multiple threads share a socket file descriptor:

- The kernel acquires a **lock on the socket structure** for each `send()` to
  ensure atomic writes and prevent data interleaving
- **Wait queues** track which threads are blocked on a socket; when data
  arrives in an empty receive queue, the kernel wakes blocked readers

## Monitoring with ss

The `ss` utility exposes queue depths in real time:

```bash
ss -xl # Show Send-Q and Recv-Q for Unix domain sockets
```

| Symptom                  | Bottleneck                                 |
|--------------------------|--------------------------------------------|
| Recv-Q consistently high | Consumer too slow to drain incoming data   |
| Send-Q consistently high | Peer's recv buffer full, throttling sender |

## Related

- [Unix domain sockets](unix-domain-sockets.md) - Data flow overview
- [UDS lifecycle](uds-lifecycle.md) - API calls for read/write
- [UDS vs TCP loopback](uds-vs-tcp-loopback.md) - Why direct copy is faster

---

Return to [Unix domain sockets](_index.md)
