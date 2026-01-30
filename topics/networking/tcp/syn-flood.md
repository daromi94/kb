# SYN Flood Attack

A SYN flood exploits TCP's stateful handshake to exhaust server resources. It's
one of the most common DDoS attack vectors.

## The Attack

1. Attacker sends thousands of SYN packets with spoofed source IPs
2. Server allocates memory (half-open connection state) for each SYN
3. Server sends SYN-ACK to spoofed addresses (never receive reply)
4. Server waits for ACK that never comes
5. Half-open connection table fills up
6. Server cannot accept legitimate connections

```
Attacker                              Server
   |                                   |
   |---- SYN (spoofed IP) ------------>|  allocate state
   |---- SYN (spoofed IP) ------------>|  allocate state
   |---- SYN (spoofed IP) ------------>|  allocate state
   |---- ... thousands more ... ------>|  memory exhausted
   |                                   |
Legitimate                             |
   |---- SYN ------------------------->|  DROPPED (no room)
```

## Defense: SYN Cookies

Linux uses SYN cookies to handle SYN floods without storing state.

**How it works**:

1. Server encodes connection info (IPs, ports, timestamp) into the ISN
   (Initial Sequence Number) itself, the "cookie"
2. Server sends SYN-ACK with this encoded ISN
3. **No state stored** at this point
4. If client sends valid ACK (cookie + 1), server can reconstruct the
   connection state and allocate memory

**Trade-off**: Some TCP options (like SACK, window scaling) cannot be
preserved in the cookie, so performance may be slightly reduced.

## Enabling SYN Cookies

```bash
# Usually enabled by default in modern Linux
sysctl net.ipv4.tcp_syncookies
# 1 = enabled

# Backlog queue size before triggering SYN cookies
sysctl net.ipv4.tcp_max_syn_backlog
```

## Other Mitigations

| Technique            | Description                          |
|----------------------|--------------------------------------|
| Rate limiting        | Limit SYNs per source IP at firewall |
| Increase backlog     | Larger queue before dropping         |
| Reduce SYN-ACK retry | `tcp_synack_retries` (default 5)     |
| Hardware/cloud scrub | Filter attack traffic upstream       |

## Related

- [Connection Lifecycle](connection-lifecycle.md) - The three-way handshake
- [TCP State Machine](state-machine.md) - SYN_RCVD state
