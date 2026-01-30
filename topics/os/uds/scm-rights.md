# SCM_RIGHTS

The killer feature of Unix Domain Sockets: passing open file descriptors
between processes.

## Why This Is Special

A file descriptor is just an integer index into a process's file table. If
Process A sends the integer `4` to Process B over a normal channel, Process B
cannot use it—their file tables are independent.

`SCM_RIGHTS` makes the kernel perform magic:

```
Process A (fd=4)              Kernel                    Process B
+---------------+        +---------------+        +---------------+
| fd table      |        |               |        | fd table      |
| 4 -> file*  --|------->| file struct   |<-------|- 7 -> file*   |
+---------------+        | refcount: 2   |        +---------------+
                         +---------------+
```

1. Kernel takes the file struct that Process A's fd points to
2. Creates a **new** fd in Process B's table pointing to the **same** struct
3. Increments the reference count

Process B receives a different integer (e.g., `7`) but it points to the same
underlying file.

## How to Use It

Requires `sendmsg()`/`recvmsg()` with ancillary data (control messages).

```c
struct msghdr msg = {0};
struct cmsghdr *cmsg;
char buf[CMSG_SPACE(sizeof(int))];

msg.msg_control = buf;
msg.msg_controllen = sizeof(buf);

cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));
*((int *)CMSG_DATA(cmsg)) = fd_to_send;

sendmsg(socket_fd, &msg, 0);
```

## Real-World Uses

**Nginx zero-downtime upgrades:**
The old master process passes listening socket fds to the new master. New
binary accepts connections without dropping any in flight.

**Systemd socket activation:**
Systemd creates sockets at boot and holds them. When a service starts, systemd
passes the already-listening fd. Service starts instantly without bind/listen
delay.

**Container runtimes:**
Pass fds for namespaces, cgroups, or pre-opened files to sandboxed processes.

**Database connection pooling:**
PgBouncer-style proxies can pass established connections between worker
processes.

## What Can Be Passed

Any file descriptor:

- Regular files
- Sockets (including other UDS)
- Pipes
- Device files
- eventfd, timerfd, signalfd

## Limitations

- Only works over UDS (TCP cannot do this)
- Both processes must be on the same host
- Receiver must handle the fd arriving with a different number

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [SO_PEERCRED](so-peercred.md) - The other UDS-only feature
- [UDS lifecycle](uds-lifecycle.md) - Using sendmsg/recvmsg
