# TCP Overview

TCP (Transmission Control Protocol) operates at the Transport Layer (Layer 4) and
provides reliable, ordered data delivery over IP's unreliable packet-switched
network.

## Core Properties

| Property            | Description                                           |
|---------------------|-------------------------------------------------------|
| Connection-oriented | Requires formal handshake before data transfer        |
| Reliable            | Guarantees delivery via ACKs and retransmission       |
| Ordered             | Guarantees byte order via sequence numbers            |
| Full-duplex         | Data flows both directions independently              |
| Stream-based        | No message boundaries (see [TCP Streams](streams.md)) |

## Header Overhead

TCP headers are minimum 20 bytes containing source/destination ports, sequence
and acknowledgment numbers, flags, and window size. Options can extend this.

## Trade-offs vs UDP

TCP's reliability comes at a cost:

- **Latency**: Handshake adds round-trip before data transfer
- **Overhead**: Header size, state tracking, acknowledgments
- **Head-of-line blocking**: Lost packets stall entire stream

UDP fires packets without guarantees but avoids these costs, making it suitable
for real-time applications where occasional loss is acceptable.

## Related

- [Connection Lifecycle](connection-lifecycle.md) - Handshake and termination
- [TCP Segment](segment.md) - Header structure details
- [TCP Streams](streams.md) - Stream semantics and framing
