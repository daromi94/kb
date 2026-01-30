# UDS Lifecycle

The UDS API mirrors TCP but with filesystem-specific setup and teardown.

## Server Lifecycle

```
+------------------+
|  socket()        |  Create endpoint (AF_UNIX, SOCK_STREAM)
+------------------+
         |
         v
+------------------+
|  unlink()        |  Remove stale socket file (UDS-specific)
+------------------+
         |
         v
+------------------+
|  bind()          |  Create socket file on disk
+------------------+
         |
         v
+------------------+
|  chmod()         |  Set permissions (optional but common)
+------------------+
         |
         v
+------------------+
|  listen()        |  Mark as passive, set backlog
+------------------+
         |
         v
+------------------+
|  accept()        |  Block until client connects
+------------------+
```

### Key Differences from TCP

**`unlink()` before bind:** If the socket file exists from a previous crash,
`bind()` fails with `EADDRINUSE`. Always unlink first.

**`bind()` creates a file:** The kernel creates an actual file at `sun_path`.
Process umask affects permissions.

**`chmod()` for security:** Control who can connect via file permissions.

## Client Lifecycle

```
+------------------+
|  socket()        |  Create endpoint (AF_UNIX, SOCK_STREAM)
+------------------+
         |
         v
+------------------+
|  connect()       |  Connect to server's socket file
+------------------+
```

### What connect() Does

1. VFS lookup for socket file inode
2. Check file permissions (client needs write access)
3. Verify file is actually a socket
4. Place client in server's listen queue

## Data Transfer

Once connected, "client" and "server" distinction disappears. Both hold file
descriptors pointing to each other.

**Standard I/O:**
```c
write(fd, "Hello", 5);  // Copy to kernel buffer
read(fd, buf, 100);     // Read from kernel buffer
```

**Advanced I/O:** Use `sendmsg()`/`recvmsg()` for ancillary data like file
descriptors (`SCM_RIGHTS`) or credentials (`SCM_CREDENTIALS`).

## Complete Flow

```
      SERVER                              CLIENT
      ------                              ------
1. socket() -> fd=3
2. unlink("/tmp/x.sock")
3. bind(fd=3, "/tmp/x.sock")
   [Kernel creates file]
4. listen(fd=3)
5. accept(fd=3) ... blocks
                                    1. socket() -> fd=4
                                    2. connect(fd=4, "/tmp/x.sock")
                                       [Permission check]
                                       [Queue insertion]

   accept returns fd=5  <------------- [Connected]

6. read(fd=5)  <--------------------- 3. write(fd=4, "Hello")
   [RAM-to-RAM copy]

7. close(fd=5)                        4. close(fd=4)
```

## API Comparison

| API       | TCP Behavior            | UDS Behavior             |
| --------- | ----------------------- | ------------------------ |
| `socket`  | `AF_INET`               | `AF_UNIX`                |
| `bind`    | Reserve port            | **Create file** on disk  |
| `connect` | TCP handshake (SYN/ACK) | Permission check + queue |
| `read`    | Network buffers         | Direct memory buffers    |
| `close`   | FIN/ACK handshake       | Immediate refcount drop  |

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [UDS socket types](uds-socket-types.md) - STREAM vs DGRAM vs SEQPACKET
- [SCM_RIGHTS](scm-rights.md) - sendmsg/recvmsg for FD passing
