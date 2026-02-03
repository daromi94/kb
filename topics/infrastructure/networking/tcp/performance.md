# TCP Performance

Modern TCP includes various optimizations and tuning options for high-throughput
and low-latency scenarios.

## Window Scaling (RFC 1323)

**Problem**: Original 16-bit window field limits to 64KB. On high-bandwidth,
high-latency links, this is far too small.

```
BDP = Bandwidth × RTT
1 Gbps × 100ms = 12.5 MB needed
```

**Solution**: During handshake, both sides negotiate a shift factor. Actual
window = header value × 2^scale. Allows windows up to 1GB.

## Nagle's Algorithm and TCP_NODELAY

**Nagle's algorithm** (default on): Buffers small writes, waiting briefly to
batch them into larger segments. Reduces "tinygram" overhead.

**Problem**: Adds latency for interactive applications.

**Solution**: Disable with `TCP_NODELAY` socket option.

```c
int flag = 1;
setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
```

**Use TCP_NODELAY for**: SSH, databases (Cassandra, ScyllaDB), real-time games,
trading systems.

## TCP Fast Open (TFO)

**Innovation**: Allows data in the SYN packet (after first connection). Saves
one RTT on connection establishment.

1. First connection: normal handshake, server provides cookie
2. Subsequent connections: client sends SYN + cookie + data
3. Server validates cookie, processes data immediately

Significant for short-lived HTTPS connections.

## Hardware Offloading

Modern NICs perform TCP work in hardware, reducing CPU load.

**TSO (TCP Segmentation Offload)**: CPU builds large (64KB) segments; NIC
hardware chops into MTU-sized packets and calculates checksums. `tcpdump` shows
impossibly large packets because it captures pre-segmentation.

**LRO (Large Receive Offload)**: NIC coalesces received packets into larger
buffers before interrupting CPU.

## Listen Backlog (somaxconn)

When SYN arrives, kernel completes handshake and queues connection for
`accept()`. If the application is slow (GC pause), the queue fills and new
SYNs are dropped silently.

```bash
# Increase backlog for high-traffic servers
sysctl -w net.core.somaxconn = 65535
```

## Zero-Copy I/O

Standard path: Disk → Kernel buffer → User space → Kernel buffer → NIC

**sendfile()**: Disk → Kernel buffer → NIC (bypasses user space copy)

**io_uring + registered buffers**: Further reduces syscall and copy overhead

## Buffer Tuning

```bash
# View TCP buffer settings (min default max)
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem

# Increase for high-BDP links
sysctl -w net.ipv4.tcp_rmem="4096 131072 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 131072 16777216"
```

## Related

- [Flow Control](flow-control.md) - Window mechanics
- [Congestion Control](congestion-control.md) - cwnd and algorithms
- [TCP Sockets](sockets.md) - Buffer interaction
