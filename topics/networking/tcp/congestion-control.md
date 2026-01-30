# TCP Congestion Control

While flow control prevents overwhelming the receiver, congestion control
prevents overwhelming the network. TCP treats packet loss as a signal of
network congestion.

## Congestion Window (cwnd)

The sender maintains a congestion window limiting bytes in flight,
**independent** of the receiver's advertised window. The effective limit is:

```
send_limit = min(cwnd, receiver_window)
```

## Slow Start

New connections have no knowledge of network capacity. Slow start probes
conservatively with exponential growth.

1. Start with small cwnd (typically 10 segments in modern Linux)
2. For each ACK received, increase cwnd by 1 segment
3. Effect: cwnd doubles each RTT (1 → 2 → 4 → 8 → 16...)
4. Continue until packet loss or ssthresh (slow start threshold) reached

**Cold connection penalty**: New connections are slow. This is why connection
pooling and HTTP persistent connections matter, keeping cwnd "warm."

## Congestion Avoidance

After slow start threshold, growth becomes linear (additive increase) to probe
more cautiously. On packet loss, cwnd is reduced aggressively (multiplicative
decrease).

## Algorithms

| Algorithm     | Loss Detection  | Behavior                        |
| ------------- | --------------- | ------------------------------- |
| Reno          | Packet loss     | Cut cwnd by 50% on loss         |
| CUBIC (Linux) | Packet loss     | Cubic function recovery, faster |
| BBR (Google)  | RTT + bandwidth | Models pipe capacity, not loss  |

**Reno**: Classic loss-based. Simple but reacts slowly on high-BDP networks.

**CUBIC**: Default on Linux. Uses cubic function for window growth, recovers
faster from loss, more stable on high-latency links.

**BBR**: Measures actual bottleneck bandwidth and RTT to send exactly what the
network can handle. Key insight: packet loss ≠ congestion (could be random
noise). Prevents bufferbloat in router queues.

## Observing cwnd

```bash
ss -ti | grep cwnd
# cwnd:10 ssthresh:20 rtt:5/3
```

## Related

- [Flow Control](flow-control.md) - Receiver-side throttling
- [Reliability](reliability.md) - Retransmission triggers
- [TCP Performance](performance.md) - Tuning options
