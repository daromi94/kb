# Partial I/O

A `read()` or `write()` on a stream socket can transfer fewer bytes than
requested. This is standard behavior, not an error — robust code must handle
it.

## Why it happens

The kernel's send and receive queues are finite. System calls bridge
application memory and these buffers, transferring only what fits or what is
available.

**Partial write:** The application requests 100 KB but the send queue has
40 KB free. On a blocking socket the kernel writes 40 KB then sleeps until
space opens, but a signal can interrupt the sleep and return a short count.
On a non-blocking socket the kernel writes 40 KB and returns immediately.

**Partial read:** The application requests 10 KB but only 2 KB sits in the
receive queue. The kernel copies the available 2 KB and returns rather than
waiting for more data (unless `MSG_WAITALL` is set).

## Return value semantics

The return value of `read()` and `write()` is the **short count** — the actual
number of bytes transferred:

| Return value     | Meaning                        |
|------------------|--------------------------------|
| Positive integer | Bytes successfully transferred |
| `0` from read    | Peer closed connection (EOF)   |
| `-1`             | Error occurred (check `errno`) |

## Common causes

| Cause                | Effect                                                                           |
|----------------------|----------------------------------------------------------------------------------|
| Signal interrupts    | Call returns bytes processed before signal                                       |
| Buffer pressure      | `SO_SNDBUF` / `SO_RCVBUF` limit reached                                          |
| Stream fragmentation | `SOCK_STREAM` has no message boundaries — the kernel splits data at buffer edges |

## Datagram exception

`SOCK_DGRAM` sockets are **atomic**. A `send()` either transmits the entire
message or fails with `EMSGSIZE` if it exceeds the buffer. Partial datagrams
never occur.

## Related

- [Socket buffers](socket-buffers.md) - Kernel queues that cause short counts
- [UDS socket types](uds-socket-types.md) - Stream vs datagram atomicity

---

Return to [Unix domain sockets](_index.md)
