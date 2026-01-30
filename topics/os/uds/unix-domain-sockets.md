# Unix Domain Sockets

A Unix Domain Socket (UDS) is an inter-process communication mechanism that
allows bidirectional data exchange between processes on the same host. While
UDS uses the standard BSD socket API (`socket`, `bind`, `connect`, `accept`),
it is fundamentally different from network sockets.

## Key Characteristics

| Aspect     | Network Socket    | Unix Domain Socket        |
| ---------- | ----------------- | ------------------------- |
| Family     | `AF_INET`         | `AF_UNIX` (or `AF_LOCAL`) |
| Addressing | IP address + port | Filesystem path           |
| Data path  | Network stack     | Direct kernel memory copy |
| Scope      | Network-reachable | Same host only            |

## The Address Structure

```c
struct sockaddr_un {
    sa_family_t sun_family;  /* AF_UNIX */
    char        sun_path[108];  /* Pathname */
};
```

**Path length constraint:** The 108-character limit is historical. Deeply
nested paths (common in Kubernetes volumes) can cause `bind()` to fail.

## How Data Flows

Data never touches a network card:

1. Sender calls `send()` with data in userspace buffer
2. Kernel copies data to internal buffer
3. Kernel copies from buffer to receiver's `recv()` buffer

No headers, checksums, sequence numbers, or acknowledgments after initial
connection.

## Common Examples

- `/var/run/docker.sock` - Docker daemon
- `/var/run/mysqld/mysqld.sock` - MySQL
- `/tmp/.X11-unix/X0` - X11 display server

## Related

- [UDS vs TCP loopback](uds-vs-tcp-loopback.md) - Why UDS is faster
- [UDS lifecycle](uds-lifecycle.md) - API calls for server and client
- [SCM_RIGHTS](scm-rights.md) - Passing file descriptors
