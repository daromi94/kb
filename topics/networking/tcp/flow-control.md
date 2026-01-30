# TCP Flow Control

Flow control prevents a fast sender from overwhelming a slow receiver's buffer.
TCP implements this through the sliding window mechanism.

## The Sliding Window

Every ACK packet includes a **Window Size** field advertising how many bytes
the receiver can currently accept.

```
Byte stream:
[Sent & ACKed][Sent, unACKed][  Usable Window  ][Cannot send yet]
              |<---- In flight ---->|
              |<-------- Receiver's advertised window -------->|
```

As ACKs arrive, the window "slides" right, allowing new data to be sent.

## Buffer Interaction

The window directly reflects free space in the kernel receive buffer:

1. Sender writes data; TCP transmits segments
2. Receiver's kernel places data in receive buffer (`SO_RCVBUF`)
3. Application calls `read()`, consuming buffer space
4. Freed space increases advertised window in next ACK

**If the application is slow to read** (e.g., processing data, GC pause), the
buffer fills up and the window shrinks.

## Zero Window

When the receive buffer is completely full, the receiver advertises **Window=0**.
The sender must stop transmitting immediately.

**Recovery**: The sender enters "persist mode," periodically sending 1-byte
probe packets. When the receiver's application reads data and frees buffer
space, it sends a **Window Update** and transmission resumes.

## Buffer Sizing

```bash
# View current buffer sizes
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem

# Format: min default max (bytes)
# net.ipv4.tcp_rmem = 4096 131072 6291456
```

**Bandwidth-Delay Product**: For high-bandwidth, high-latency links, buffers
must be large enough to keep the pipe full:

```
BDP = Bandwidth × RTT
1 Gbps × 100ms = 12.5 MB
```

The default 64KB window is far too small. Window Scaling option (RFC 1323)
allows windows up to 1GB by applying a shift factor negotiated during
handshake.

## Related

- [TCP Segment](segment.md) - Window Size field
- [Congestion Control](congestion-control.md) - Network-side throttling
- [TCP Sockets](sockets.md) - Kernel buffer interaction
