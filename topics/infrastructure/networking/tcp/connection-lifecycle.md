# Connection lifecycle

TCP connections follow a strict state machine with formal establishment and
termination sequences.

## Establishment: three-Way handshake

Before data transfer, client and server must agree on initial sequence numbers.

```text
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

## Termination: four-Way wave

Because TCP is full-duplex, each side must terminate its sending capability
independently.

```text
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

---

Return to [TCP](_index.md)
