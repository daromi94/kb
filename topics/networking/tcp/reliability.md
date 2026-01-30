# TCP Reliability

TCP creates the illusion of a reliable stream over IP's unreliable
packet-switched network using sequence numbers and acknowledgments.

## Sequence Numbers

Every byte in the stream has a sequence number. The sender includes the
sequence number of the first data byte in each segment.

**Purpose:**

- Receiver reassembles out-of-order packets correctly
- Detects duplicate packets (retransmissions that arrived late)
- 32-bit field wraps after 4GB of data

## Acknowledgments

The receiver sends ACKs indicating the sequence number of the **next byte it
expects**. This implicitly acknowledges all prior bytes.

```
Sender                              Receiver
   |                                   |
   |---- seq=1000, 100 bytes --------->|
   |                                   |
   |<--- ack=1100 ---------------------|  "Got it, send 1100 next"
   |                                   |
   |---- seq=1100, 100 bytes --------->|
   |                                   |
   |<--- ack=1200 ---------------------|
```

## Retransmission

If the sender doesn't receive an ACK within the Retransmission Timeout (RTO),
it assumes the packet was lost and retransmits.

**RTO calculation**: Based on measured Round Trip Time (RTT) with smoothing to
handle variance. Too short causes spurious retransmissions; too long delays
recovery.

## Selective Acknowledgment (SACK)

Standard ACKs can only indicate "I have everything up to X." If packet 2 of 5
is lost, the receiver can only ACK packet 1, potentially causing retransmission
of packets 3-5 unnecessarily.

**SACK option** allows the receiver to report non-contiguous blocks:

```
"I have 1, and I also have the block 3-5"
```

The sender retransmits **only** packet 2, dramatically improving efficiency on
lossy links.

## Checksums

Every segment includes a 16-bit checksum covering both header and data (plus a
pseudo-header with IP addresses). Corrupted segments are silently dropped,
triggering retransmission via timeout.

## Related

- [TCP Segment](segment.md) - Sequence and ACK fields in header
- [Congestion Control](congestion-control.md) - How retransmission interacts
  with congestion algorithms
