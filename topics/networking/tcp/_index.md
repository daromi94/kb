# TCP

Transmission Control Protocol - reliable, ordered, connection-oriented transport
over IP.

## Notes

- [Overview](overview.md) - Core properties and trade-offs vs UDP
- [Connection Lifecycle](connection-lifecycle.md) - Three-way handshake and four-way termination
- [TCP Segment](segment.md) - Header structure, fields, flags, and options
- [TCP State Machine](state-machine.md) - States with focus on TIME_WAIT and CLOSE_WAIT
- [Reliability](reliability.md) - Sequence numbers, ACKs, retransmission, SACK
- [Flow Control](flow-control.md) - Sliding window and buffer interaction
- [Congestion Control](congestion-control.md) - Slow start, cwnd, Reno/CUBIC/BBR
- [TCP Streams](streams.md) - No message boundaries and framing strategies
- [TCP Sockets](sockets.md) - Kernel interaction, buffers, socket options
- [TCP Keepalives](keepalives.md) - Detecting dead connections
- [TCP Performance](performance.md) - Window scaling, Nagle, TFO, offloading, tuning
- [Head-of-Line Blocking](head-of-line-blocking.md) - TCP's fundamental limitation
- [SYN Flood](syn-flood.md) - DDoS attack and SYN cookies defense
- [Statefulness](statefulness.md) - TCB memory costs and load balancing implications
