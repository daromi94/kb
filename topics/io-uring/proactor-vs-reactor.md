# Proactor vs reactor

Two fundamental patterns for handling asynchronous I/O operations.

## Reactor pattern (readiness-based)

Used by `epoll`, `kqueue`, and most event loops (Node.js, Nginx).

**Model:** "Tell me when I can read."

The application asks the OS to monitor file descriptors. When data is available
(ready), the OS notifies the app, which then performs the actual read/write.

```
App: "Watch this socket"
OS:  "Socket is ready to read"
App: read(socket, buffer)  // App does the I/O
```

## Proactor pattern (completion-based)

Used by `io_uring` and Windows IOCP.

**Model:** "Do this read and tell me when you're done."

The application submits the I/O operation itself. The OS performs the operation
and notifies when complete.

```
App: "Read from this socket into this buffer"
OS:  [performs read asynchronously]
OS:  "Read complete, 1024 bytes in buffer"
```

## Comparison

| Aspect            | Reactor (epoll)                      | Proactor (io_uring)                    |
|-------------------|--------------------------------------|----------------------------------------|
| Notification      | "Ready to read"                      | "Read complete"                        |
| Who does I/O      | Application                          | OS/Kernel                              |
| Syscalls          | epoll_wait + read/write per chunk    | One io_uring_enter for batches         |
| Disk I/O          | No true async (files always "ready") | Full async disk support                |
| Buffer management | Per read/write call                  | Can register/pin for efficiency        |
| Complexity        | Moderate                             | High (memory barriers, liburing helps) |

## Why proactor is faster

**Syscall reduction:** Reactor requires two syscalls per operation (wait +
read). Proactor batches many operations into one submission.

**True disk async:** epoll cannot do async disk I/O because files are always
reported as "ready". io_uring handles disk operations asynchronously.

**Buffer pinning:** Proactor can register buffers once and reuse them, avoiding
per-operation memory management overhead.

## Related

- [io_uring](io-uring.md) - Linux proactor implementation
- [Asynchronous I/O](../async-io/asynchronous-io.md) - General async concepts
