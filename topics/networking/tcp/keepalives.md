# TCP Keepalives

TCP connections can sit idle indefinitely. If a peer crashes or the network
path breaks while no data is flowing, the other side will never know. Keepalive
probes detect these "dead peers."

## The Problem

TCP is silent by default. If you unplug a server's cable during idle time, the
client's socket remains ESTABLISHED forever, consuming memory and file
descriptors.

## How Keepalives Work

1. **Idle timer**: After no data for `tcp_keepalive_time` (default: 2 hours),
   kernel wakes up
2. **Probe**: Sends empty ACK packet to peer
3. **Response**:
   - Peer ACKs → connection alive, reset timer
   - Peer sends RST → peer rebooted, close connection
   - No reply → retry `tcp_keepalive_probes` times at `tcp_keepalive_intvl`
     intervals
4. **Failure**: After all probes fail, kernel closes connection with ETIMEDOUT

## Linux Tuning

Default 2-hour wait is unacceptable for high-availability systems.

```bash
# /etc/sysctl.conf

# Start probing after 60 seconds of silence (default 7200)
net.ipv4.tcp_keepalive_time = 60

# Wait 10 seconds between probes (default 75)
net.ipv4.tcp_keepalive_intvl = 10

# Give up after 3 failed probes (default 9)
net.ipv4.tcp_keepalive_probes = 3
```

Total detection time: 60 + (10 × 3) = 90 seconds

## Enabling Keepalives

Keepalives are disabled by default. Enable per-socket:

```c
int optval = 1;
setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval));
```

Or in application frameworks (Java, Python, etc.) via socket options.

## TCP vs HTTP Keep-Alive

These are completely different concepts:

| Term            | Purpose                                  |
| --------------- | ---------------------------------------- |
| TCP Keepalive   | Detect dead connections (liveness probe) |
| HTTP Keep-Alive | Reuse connection for multiple requests   |

## Application-Level Heartbeats

For finer control, many protocols implement their own heartbeats:

- Faster detection than TCP keepalives
- Application-aware (can verify service health, not just TCP)
- Works through NAT/proxies that may intercept TCP keepalives

Examples: gRPC keepalive pings, WebSocket ping/pong, database connection pools

## Related

- [TCP State Machine](state-machine.md) - Connection states
- [TCP Sockets](sockets.md) - Socket options
