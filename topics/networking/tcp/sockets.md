# TCP Sockets

Applications interact with TCP through the socket API. The kernel mediates
between user-space operations and the protocol state machine.

## Architecture

```
+-----------------------------------------------------------+
|  User Space                                               |
|    Application (file descriptor fd=3)                     |
|         |                          ^                      |
|         | write()                  | read()               |
|         v                          |                      |
+-----------------------------------------------------------+
|  Kernel Space                                             |
|    +----------------+         +----------------+          |
|    |  Send Buffer   |         |  Recv Buffer   |          |
|    |  (SO_SNDBUF)   |         |  (SO_RCVBUF)   |          |
|    +-------+--------+         +--------^-------+          |
|            |                           |                  |
|            | TCP segmentation          | TCP reassembly   |
|            v                           |                  |
+-----------------------------------------------------------+
|  NIC (DMA)                                                |
|            |                           ^                  |
|            +------ network wire -------+                  |
+-----------------------------------------------------------+
```

## System Call Behavior

### connect()

```c
connect(fd, target_addr, len);
```

1. Kernel allocates TCB (Transmission Control Block)
2. Sends SYN, sets state to SYN_SENT
3. **Thread blocks** until SYN-ACK received and ACK sent
4. Returns when ESTABLISHED (or error on RST/timeout)

### write()

```c
write(fd, data, len);
```

**Misconception**: `write()` does not send data to the network.

**Reality**: `write()` copies data to the kernel send buffer. TCP asynchronously
segments and transmits it.

- If buffer has space: returns immediately
- If buffer full: **blocks** until ACKs free space

### read()

```c
read(fd, buffer, len);
```

Copies data from kernel receive buffer to user space.

- If data available: returns immediately with available bytes
- If buffer empty: **blocks** until data arrives

Reading frees buffer space, increasing the advertised window.

## Socket Options

| Option       | Purpose                                      |
| ------------ | -------------------------------------------- |
| TCP_NODELAY  | Disable Nagle's algorithm (send immediately) |
| SO_REUSEADDR | Allow bind to port in TIME_WAIT              |
| SO_LINGER    | Block on close() until FIN acknowledged      |
| SO_KEEPALIVE | Enable TCP keepalive probes                  |
| SO_SNDBUF    | Set send buffer size                         |
| SO_RCVBUF    | Set receive buffer size                      |

## Inspecting Socket State

```bash
ss -ti
# State    Recv-Q Send-Q  Local:Port    Peer:Port
# ESTAB    0      1460    10.0.0.1:443  192.168.1.5:52341
#     cwnd:10 ssthresh:20 unacked:1 rto:204 rtt:5/3 mss:1460
```

| Field  | Meaning                                   |
| ------ | ----------------------------------------- |
| Recv-Q | Bytes in receive buffer (app hasn't read) |
| Send-Q | Bytes in send buffer (not yet ACKed)      |
| cwnd   | Current congestion window                 |
| rto    | Retransmission timeout (ms)               |
| rtt    | Measured round-trip time                  |

## Related

- [Flow Control](flow-control.md) - Buffer and window interaction
- [TCP Keepalives](keepalives.md) - Detecting dead peers
- [TCP Performance](performance.md) - Buffer tuning
