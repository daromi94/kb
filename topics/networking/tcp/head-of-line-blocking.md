# TCP Head-of-Line Blocking

Head-of-line (HOL) blocking is TCP's fundamental limitation and the primary
reason the industry is moving toward UDP-based protocols like QUIC.

## The Problem

TCP guarantees **ordered delivery**. If any packet is lost, the kernel buffers
all subsequent packets until the missing one is retransmitted.

**Scenario**: Browser loads a page with 5 images over one TCP connection:

```
        Packet 1 (Image 1, part A)  ✓
        Packet 2 (Image 1, part B)  ✗ LOST
        Packet 3 (Image 2)          ✓ (buffered, waiting)
        Packet 4 (Image 3)          ✓ (buffered, waiting)
        Packet 5 (Image 4)          ✓ (buffered, waiting)
```

**Result**: Images 2, 3, and 4 arrived perfectly but cannot be delivered to
the application until Image 1's lost packet is retransmitted. One lost packet
stalls the entire stream.

## Why This Happens

TCP's stream abstraction guarantees bytes arrive in order. The kernel cannot
deliver byte 1001 until bytes 1-1000 are complete. This is a feature for
some applications but a bug for multiplexed protocols.

## HTTP/2's Workaround

HTTP/2 multiplexes multiple logical streams over one TCP connection. But HOL
blocking at the TCP layer still affects all streams when any packet is lost.

## QUIC's Solution

QUIC runs over UDP and implements its own reliability. Each stream has
independent ordering, so a lost packet only blocks its own stream:

```
QUIC Stream 1: packet lost → Stream 1 waits
QUIC Stream 2: packets arrived → delivered immediately
QUIC Stream 3: packets arrived → delivered immediately
```

This is why HTTP/3 (which uses QUIC) performs better on lossy networks.

## When HOL Blocking Matters

| Scenario             | Impact                              |
|----------------------|-------------------------------------|
| Single request/reply | Minimal (only one stream)           |
| Multiplexed streams  | Severe (all streams blocked)        |
| Lossy networks       | Severe (frequent retransmissions)   |
| Real-time data       | Severe (stale data still delivered) |

## Related

- [Reliability](reliability.md) - TCP's ordering guarantee
- [TCP Streams](streams.md) - Stream abstraction
