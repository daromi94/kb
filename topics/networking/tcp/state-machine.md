# TCP State Machine

TCP connections transition through well-defined states. Two states are
particularly important for diagnosing system issues.

## Key States

| State       | Description                                      |
|-------------|--------------------------------------------------|
| LISTEN      | Server waiting for connection requests           |
| SYN_SENT    | Client sent SYN, awaiting SYN-ACK                |
| SYN_RCVD    | Server received SYN, sent SYN-ACK, awaiting ACK  |
| ESTABLISHED | Connection open, data transfer active            |
| FIN_WAIT_1  | Sent FIN, awaiting ACK                           |
| FIN_WAIT_2  | FIN acknowledged, awaiting peer's FIN            |
| CLOSE_WAIT  | Received FIN, awaiting application close         |
| LAST_ACK    | Sent FIN after receiving FIN, awaiting final ACK |
| TIME_WAIT   | Waiting for delayed packets to expire            |
| CLOSED      | No connection                                    |

## CLOSE_WAIT: The Application Leak

When the remote side sends FIN, the kernel ACKs it and enters CLOSE_WAIT. The
connection remains here until **your application** calls `close()`.

**Thousands of CLOSE_WAIT sockets indicate an application bug**: the code is
failing to close connections properly, leaking file descriptors.

## TIME_WAIT: The Safety Net

After sending the final ACK, the active closer enters TIME_WAIT for 2×MSL
(Maximum Segment Lifetime), typically 60 seconds.

**Why it exists:**

1. **Delayed packets**: Prevents old packets from a previous connection being
   accepted by a new connection on the same port tuple
2. **ACK reliability**: If the final ACK was lost, the peer will resend FIN;
   the socket must remain to respond

**The danger**: High-traffic load balancers can exhaust ephemeral ports because
they're tied up in TIME_WAIT.

**Mitigation**: Tune with `sysctl`:

```bash
# Allow reuse of TIME_WAIT sockets for new connections
net.ipv4.tcp_tw_reuse = 1
```

## Inspecting States

```bash
# View socket states
ss -tan state time-wait
ss -tan state close-wait | wc -l
netstat -an | grep CLOSE_WAIT
```

## Related

- [Connection Lifecycle](connection-lifecycle.md) - Handshake and termination
- [TCP Keepalives](keepalives.md) - Detecting dead connections
