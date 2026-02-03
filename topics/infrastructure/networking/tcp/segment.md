# TCP Segment Structure

Every TCP segment consists of a header (minimum 20 bytes) followed by optional
data payload.

## Header Fields

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |       |C|E|U|A|P|R|S|F|                               |
| Offset| Rsrvd |W|C|R|C|S|S|Y|I|            Window             |
|       |       |R|E|G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options (variable)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

## Field Details

| Field            | Bits | Description                                      |
|------------------|------|--------------------------------------------------|
| Source Port      | 16   | Sender's port (forms 5-tuple with IPs)           |
| Destination Port | 16   | Receiver's port                                  |
| Sequence Number  | 32   | Byte position in stream (ISN if SYN set)         |
| Ack Number       | 32   | Next expected byte (valid when ACK flag set)     |
| Data Offset      | 4    | Header length in 32-bit words (min 5 = 20 bytes) |
| Window Size      | 16   | Receive buffer space (flow control)              |
| Checksum         | 16   | Error detection (covers pseudo-header too)       |
| Urgent Pointer   | 16   | End of urgent data (when URG set, rarely used)   |

## Control Flags

| Flag | Purpose                                         |
|------|-------------------------------------------------|
| SYN  | Synchronize sequence numbers (connection start) |
| ACK  | Acknowledgment field is valid                   |
| FIN  | No more data from sender (connection close)     |
| RST  | Reset connection immediately (abort)            |
| PSH  | Push buffered data to application immediately   |
| URG  | Urgent pointer field is valid                   |
| ECE  | ECN-Echo (congestion notification)              |
| CWR  | Congestion Window Reduced                       |

## Common Options

| Option       | Purpose                                           |
|--------------|---------------------------------------------------|
| MSS          | Maximum Segment Size (sent only in SYN)           |
| Window Scale | Multiply window by 2^n (allows windows > 64KB)    |
| SACK         | Selective acknowledgment of non-contiguous blocks |
| Timestamps   | RTT measurement and PAWS protection               |

## Related

- [Reliability](reliability.md) - How sequence numbers enable ordering
- [Flow Control](flow-control.md) - Window size mechanics
