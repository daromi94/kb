# TCP Statefulness

TCP is stateful: both endpoints must maintain connection state in memory. This
is fundamental to how TCP provides reliability but comes with significant costs.

## The Transmission Control Block (TCB)

For every active connection, the kernel allocates a TCB containing:

- Connection state (ESTABLISHED, FIN_WAIT, etc.)
- Sequence numbers (sent and expected)
- Window sizes (local and remote)
- Timers (retransmission, keepalive)
- Buffer pointers

If either side loses this state (crash, reboot), the connection breaks. The
next packet triggers an RST because the receiver has no memory of the
relationship.

## Comparison: Stateful vs Stateless

| Protocol | Type      | Analogy    | Description                         |
|----------|-----------|------------|-------------------------------------|
| TCP      | Stateful  | Phone call | Both sides track conversation state |
| UDP/IP   | Stateless | Mailbox    | Each packet independent, no memory  |

## Costs of Statefulness

### Memory Pressure

Every open connection consumes kernel memory. A server with 1 million
concurrent connections (C10M problem) needs significant RAM just for TCBs,
even with no data flowing.

Typical TCB size: several hundred bytes to a few KB depending on options.

### DDoS Vulnerability

Attacks like SYN floods exploit statefulness by forcing servers to allocate
state for fake connections until memory exhausts.

### Load Balancing Complexity

You cannot simply spray packets across servers. Packet 1 to Server A, Packet 2
to Server B fails because Server B lacks the connection state.

**Solutions**:

- **Session stickiness**: Route all packets for a connection to the same server
- **Stateless load balancing**: Use consistent hashing on 5-tuple
- **Connection tracking**: Load balancer maintains state (becomes bottleneck)
- **DSR (Direct Server Return)**: Only inbound goes through LB

## Stateless Alternatives

Protocols like QUIC implement reliability over UDP with connection IDs that
allow migration between paths/addresses, partially addressing the load
balancing problem.

## Related

- [TCP State Machine](state-machine.md) - Connection states
- [SYN Flood](syn-flood.md) - Exploiting statefulness
- [TCP Sockets](sockets.md) - Kernel structures
