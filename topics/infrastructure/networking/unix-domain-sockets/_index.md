# Unix Domain Sockets

Inter-process communication via the BSD socket API.

## Notes

- [Unix domain sockets](unix-domain-sockets.md) - Local IPC using socket API
- [UDS socket types](uds-socket-types.md) - Stream, datagram, and seqpacket
- [UDS lifecycle](uds-lifecycle.md) - Server and client API flow
- [Socket buffers](socket-buffers.md) - Kernel send/receive queues and tuning
- [Partial I/O](partial-io.md) - Short counts on read and write
- [UDS vs TCP loopback](uds-vs-tcp-loopback.md) - Performance comparison
- [SCM_RIGHTS](scm-rights.md) - Passing file descriptors between processes
- [SO_PEERCRED](so-peercred.md) - Kernel-level credential authentication
- [Abstract namespace](abstract-namespace.md) - Linux cleanup-free sockets
- [Common pitfalls](common-pitfalls.md) - Frequent mistakes and fixes

---

Return to [Networking](../_index.md)
