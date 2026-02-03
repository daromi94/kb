# TCP Connection Lifecycle

TCP connections follow a strict state machine with formal establishment and
termination sequences.

## Establishment: Three-Way Handshake

Before data transfer, client and server must agree on initial sequence numbers.

```
Client                              Server
   |                                   |
   |---- SYN (seq=x) ----------------->|
   |                                   |
   |<--- SYN-ACK (seq=y, ack=x+1) -----|
   |                                   |
   |---- ACK (ack=y+1) --------------->|
   |                                   |
   |         ESTABLISHED               |
```

1. **SYN**: Client sends packet with SYN flag and random Initial Sequence
   Number (ISN)
2. **SYN-ACK**: Server responds with its own ISN and acknowledges client's
   ISN+1
3. **ACK**: Client acknowledges server's ISN+1; connection established

## Termination: Four-Way Wave

Because TCP is full-duplex, each side must terminate its sending capability
independently.

```
Client                              Server
   |                                   |
   |---- FIN ------------------------->|  "I'm done sending"
   |                                   |
   |<--- ACK --------------------------|  "Got it"
   |                                   |
   |<--- FIN --------------------------|  "I'm also done"
   |                                   |
   |---- ACK ------------------------->|  "Got it"
   |                                   |
   |      TIME_WAIT (2*MSL)            |
```

The active closer enters TIME_WAIT for 2×MSL (typically 60 seconds) to handle
delayed packets and ensure the final ACK arrives.

## Related

- [TCP State Machine](state-machine.md) - States like TIME_WAIT and CLOSE_WAIT
- [TCP Segment](segment.md) - Flag fields (SYN, FIN, ACK)
