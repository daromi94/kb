# TCP

Transmission Control Protocol - reliable, ordered, connection-oriented transport
over IP.

## Notes

- [Overview](overview.md) - Core properties and trade-offs vs UDP
- [Connection lifecycle](connection-lifecycle.md) - Three-way handshake and four-way termination
- [Segment structure](segment.md) - Header structure, fields, flags, and options
- [State machine](state-machine.md) - States with focus on TIME_WAIT and CLOSE_WAIT
- [Reliability](reliability.md) - Sequence numbers, ACKs, retransmission, SACK
- [Flow control](flow-control.md) - Sliding window and buffer interaction
- [Congestion control](congestion-control.md) - Slow start, cwnd, Reno/CUBIC/BBR
- [Streams](streams.md) - No message boundaries and framing strategies
- [Sockets](sockets.md) - Kernel interaction, buffers, socket options
- [Keepalives](keepalives.md) - Detecting dead connections
- [Performance](performance.md) - Window scaling, Nagle, TFO, offloading, tuning
- [Head-of-line blocking](head-of-line-blocking.md) - TCP's fundamental limitation
- [SYN flood attack](syn-flood.md) - DDoS attack and SYN cookies defense
- [Statefulness](statefulness.md) - TCB memory costs and load balancing implications

---

Return to [Networking](../_index.md)
