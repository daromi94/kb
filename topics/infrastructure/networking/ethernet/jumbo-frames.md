# Jumbo frames

Ethernet frames with an MTU larger than the standard 1500 bytes, typically
9000 bytes. Jumbo frames reduce per-packet overhead by transmitting the same
data in fewer frames.

## Standard vs jumbo

IEEE 802.3 defines standard Ethernet with a 1500-byte payload (MTU). Adding
the Ethernet header (14 bytes), FCS (4 bytes), and optional VLAN tag
(4 bytes), total frame size is 1518-1522 bytes.

A jumbo frame raises the MTU to 9000 bytes, sending roughly six times fewer
frames for the same data volume. Fewer frames means fewer CPU interrupts,
fewer header parses, fewer checksums, and fewer inter-frame gaps.

| Aspect        | Standard (1500 B)  | Jumbo (9000 B)             |
|---------------|--------------------|----------------------------|
| CPU overhead  | Higher (more IRQs) | Lower (fewer IRQs)         |
| Efficiency    | ~95% payload ratio | ~99% payload ratio         |
| Compatibility | Universal          | Requires end-to-end config |
| Retransmit    | 1500 B per drop    | 9000 B per drop            |

## End-to-end requirement

MTU must match across the entire Layer 2 path. Every switch port, NIC, and
driver between source and destination must support the configured MTU. Layer 2
does not negotiate MTU — a switch with a 1500-byte limit silently drops
oversized frames.

In Layer 3 routed environments, Path MTU Discovery (PMTUD) relies on ICMP
"Fragmentation Needed" messages. Firewalls that block ICMP break PMTUD and
create black holes where large packets vanish with no error feedback.

## Pitfalls

**MTU mismatch black holes.** A single misconfigured switch port silently
drops jumbo frames, causing intermittent failures, hanging TCP sessions, and
timeouts that are hard to diagnose.

**Retransmission cost.** A dropped 9000-byte frame costs six times more
retransmission than a 1500-byte frame. On lossy links this stalls the TCP
congestion window.

**Serialization delay.** Larger frames take longer to serialize onto the wire,
increasing jitter for latency-sensitive traffic (VoIP, real-time control)
queued behind them.

**Diminishing returns.** NIC hardware offloading (TSO, checksum offload)
already handles much of the per-packet CPU cost that jumbo frames aim to
reduce.

## Where jumbo frames make sense

**Encapsulation headroom.** The strongest use case. Overlay protocols (VXLAN,
GRE, IPsec, QinQ) add headers that push a 1500-byte inner payload past the
standard MTU. A 9000-byte backbone MTU lets encapsulated 1500-byte host
traffic pass without fragmentation.

**Storage networks.** Dedicated VLANs carrying iSCSI or NFS bulk transfers
benefit from the reduced overhead on saturated multi-gigabit links.

**HPC clusters.** Environments with massive, rapid data synchronization
between nodes.

For general-purpose networking, the operational risk of a single misconfigured
port outweighs the marginal throughput gain.

---

Return to [Ethernet](_index.md)
