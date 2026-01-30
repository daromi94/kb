# UDS vs TCP Loopback

Connecting to `localhost:8080` (TCP) hits the network stack. Connecting to
`/tmp/app.sock` (UDS) bypasses it entirely.

## TCP Loopback Path

Even on `127.0.0.1`, a TCP packet traverses:

```
+---------------------------+
|  Application              |
|          |                |
|          | send()         |
|          v                |
+---------------------------+
|  Transport (L4)           |
|  - Segmentation           |
|  - TCP header + checksum  |
|  - Sequence numbers       |
|          |                |
|          v                |
+---------------------------+
|  Network (L3)             |
|  - IP header              |
|  - Routing table lookup   |
|          |                |
|          v                |
+---------------------------+
|  Loopback Interface (lo)  |
|          |                |
|          v                |
+---------------------------+
|  Reverse path             |
|  - Strip headers          |
|  - Verify checksums       |
|  - Reassemble stream      |
+---------------------------+
```

**Cost:** CPU overhead for encapsulation/decapsulation and context switches.

## UDS Path

```
+---------------------------+
|  Application              |
|          |                |
|          | send()         |
|          v                |
+---------------------------+
|  VFS Lookup               |
|  - Socket file inode      |
|          |                |
|          v                |
+---------------------------+
|  Direct Memory Copy       |
|  - Sender buffer          |
|  - Kernel buffer          |
|  - Receiver buffer        |
+---------------------------+
```

**Benefit:** Roughly 2x faster throughput, lower latency.

## Comparison

| Feature     | TCP Loopback             | Unix Domain Socket         |
| ----------- | ------------------------ | -------------------------- |
| OS layer    | L4 (Transport)           | VFS / Kernel memory        |
| Data flow   | Packets → Routing → lo   | Direct kernel memory copy  |
| Reliability | ACKs, retries, checksums | Inherent (memory-based)    |
| Ordering    | Sequence numbers         | Kernel FIFO buffers        |
| Addressing  | IP:Port                  | Filesystem path            |
| Security    | Firewall, TLS            | File permissions, PEERCRED |
| Special     | Can route to other hosts | Can pass file descriptors  |

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [SCM_RIGHTS](scm-rights.md) - The feature TCP cannot replicate
