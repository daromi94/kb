# Common pitfalls

Mistakes that surface repeatedly in UDS programming, along with their
standard fixes.

## Stale socket file

Unlike TCP ports, a UDS path is a physical file. If the process crashes
without calling `unlink()`, the file remains and the next `bind()` fails
with `EADDRINUSE`.

**Fix:** Always `unlink(path)` immediately before `bind()`. Add signal
handlers for graceful cleanup, but never rely on them alone.

## Assuming stream preserves boundaries

`SOCK_STREAM` is a continuous byte stream. The kernel may coalesce multiple
writes into one read or split one write across multiple reads.

**Fix:** Implement a framing protocol (e.g. 4-byte length prefix) or use
`SOCK_SEQPACKET`, which preserves message boundaries with connection
semantics.

## SIGPIPE on write to closed peer

Writing to a socket whose reader has disconnected delivers a `SIGPIPE`
signal, which terminates the process by default. If the signal is ignored
or blocked, the same `write()` or `send()` call returns -1 with `errno`
set to `EPIPE`.

**Fix:** Ignore the signal globally or suppress it per-call:

```c
// Option 1: Global (standard for most network daemons)
signal(SIGPIPE, SIG_IGN);

// Option 2: Per-call (requires send() instead of write())
send(fd, buf, len, MSG_NOSIGNAL);
```

Using `MSG_NOSIGNAL` suppresses the `SIGPIPE` for that specific call,
allowing the application to handle the disconnection via normal error
logic (`if (errno == EPIPE)`) without risking a process crash.

## Permission race on bind

`bind()` creates the socket file, then `chmod()` restricts access — but
between those calls, any local process can connect.

**Fix:** Set `umask` before `bind()` so the file is created with correct
permissions from the start:

```c
mode_t old = umask(0177); // owner-only: srw-------
bind(fd, (struct sockaddr *)&addr, sizeof(addr));
umask(old);
```

## Abstract namespace portability

The abstract namespace (paths starting with `\0`) requires no `unlink()`
and leaves no filesystem footprint, but it is Linux-only. Code using it
will fail silently or error on macOS and BSD.

**Fix:** Use filesystem paths for portable code. Reserve abstract namespace
for Linux-only internal IPC.

## SCM_RIGHTS buffer alignment

Passing file descriptors via `sendmsg()` requires correctly aligned
ancillary data buffers using `CMSG_FIRSTHDR` and `CMSG_NXTHDR`. Misaligned
buffers cause memory corruption or silent failures. The sender can safely
`close()` their FD after `sendmsg()` returns — the kernel holds a
reference.

## Socket path in /tmp

`/tmp` is world-writable. An attacker can pre-create a file at the socket
path, causing `bind()` to fail (denial of service) or, with loose
permissions, intercepting connections.

**Fix:** Use `/run` (or `/var/run`) and create a subdirectory owned by the
service user:

```
/run/my-service/service.sock
```

## Blocking accept in event loops

A bare `accept()` blocks the thread until a connection arrives. In a
single-threaded server that also handles timers or heartbeats, this stalls
all other work.

**Fix:** Set the listener non-blocking and register it with an I/O
multiplexer (`epoll`, `kqueue`, `io_uring`) so `accept()` is only called
when a connection is ready.

## Path length limit

The `sun_path` field is 108 bytes on Linux, 104 on BSD. Deeply nested
deployment paths (common in Kubernetes volumes) can exceed this.

**Fix:** Keep socket paths short. If necessary, `chdir()` into the
directory and bind with a relative path.

## Quick reference

| Pitfall            | Symptom               | Severity |
|--------------------|-----------------------|----------|
| No `unlink()`      | `EADDRINUSE`          | High     |
| Missing framing    | Merged/split messages | Medium   |
| Ignoring `SIGPIPE` | Sudden process death  | High     |
| Permission race    | Unauthorized connects | Medium   |
| Long paths         | `ENAMETOOLONG`        | Low      |

## Related

- [UDS lifecycle](uds-lifecycle.md) - Server bind/accept flow
- [UDS socket types](uds-socket-types.md) - SEQPACKET avoids framing bugs
- [Partial I/O](partial-io.md) - Short counts from buffer pressure
- [SCM_RIGHTS](scm-rights.md) - FD passing mechanics
- [Abstract namespace](abstract-namespace.md) - Linux-only convenience

---

Return to [Unix domain sockets](_index.md)
