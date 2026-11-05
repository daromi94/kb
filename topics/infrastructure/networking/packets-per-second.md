# Packets per second

**Packets Per Second (PPS) is a measure of how many network packets are transmitted, received, or processed in one second.**

It is one of the most important metrics for understanding networking performance, alongside bandwidth (bits per second) and latency.

## 1. PPS measures packet rate, not data volume

Consider a network interface receiving traffic:

```text
       Network
          |
          v
+-------------------+
|        NIC        |
+-------------------+
          |
Packet 1  |
Packet 2  |
Packet 3  |
Packet 4  |
   ...    |
          v
    Linux kernel
```

If a NIC receives 1,000,000 packets in one second, its receive rate is:

```text
PPS = 1,000,000 packets/second
```

However, PPS says nothing about how large those packets are.

A million packets might contain relatively little data if they are small, or several gigabits of data if they are large.

## 2. PPS vs. Bandwidth

Bandwidth measures the amount of data transmitted per second, typically in bits per second (bps).

PPS measures the number of individual packets transmitted per second.

The relationship is approximately:

```text
Bandwidth (bps) = PPS * Packet size (bytes) * 8
```

The packet size must be measured consistently, including or excluding protocol overhead as appropriate.

For example, consider a 10 Gbps Ethernet connection.

Approximate maximum packet rates on 10 Gbps Ethernet:

- **Minimum Ethernet frames (64 B):** 14.88 M packets/second
- **1500-byte MTU frames:** 0.813 M packets/second

Both cases can saturate the same 10 Gbps link. Calculations include Ethernet preamble, inter-frame gap, headers, and FCS, without VLAN tags.

The important observation is that **the same bandwidth can require dramatically different packet rates.**

Small packets require more packets per second to move the same amount of data.

## 3. Why does PPS matter for Linux?

Processing a network packet requires work from the NIC and operating system.

For a simplified receive path:

```text
    Network
       |
       v
+-------------+
|     NIC     |
+-------------+
       |
   DMA write
       |
       v
+-------------+
|   RX ring   |
+-------------+
       |
 NAPI polling
       |
       v
+-------------+
| Linux stack |
|             |
| Ethernet    |
| IP          |
| TCP / UDP   |
+-------------+
       |
       v
+-------------+
| Application |
+-------------+
```

Each packet may introduce processing overhead:

- Packet descriptor handling and receive-ring management.
- Kernel packet metadata management (`sk_buff`, or SKB).
- Network protocol processing.
- Routing, filtering, and connection tracking.
- Memory and CPU-cache activity.
- Queueing and synchronization.

Not all packets traverse every operation, and Linux can batch or aggregate some of this work.

Nevertheless, **packet processing has a per-packet cost, not just a per-byte cost.**

For example, suppose processing a packet costs 500 ns of CPU time on average.

At 1 million PPS:

```text
1,000,000 * 500 ns = 0.5 CPU-seconds/second
```

That is approximately 50% of one logical CPU's available execution time, assuming this cost is fully accounted for on that CPU.

At 10 million PPS, the same processing cost requires approximately five CPU-seconds per second.

This illustrates why PPS can become a bottleneck even when the network has plenty of available bandwidth.

## 4. PPS can limit throughput before bandwidth does

Consider a hypothetical machine with:

- 10 Gbps network interface.
- Packet-processing capacity of 2 million PPS.
- No other performance bottlenecks.

The effective throughput depends on packet size.

| Ethernet frame size | PPS to saturate 10 Gbps | Expected bottleneck     |
| ------------------- | ----------------------- | ----------------------- |
| 64 B                | 14.88 million           | CPU / packet processing |
| 512 B               | 2.35 million            | CPU / packet processing |
| 1518 B              | 0.813 million           | Network bandwidth       |

These figures include 20 bytes of Ethernet wire overhead per frame.

With 64-byte frames, the hypothetical machine cannot saturate the link because its packet-processing capacity is insufficient.

With 1518-byte frames, the machine can theoretically saturate the link without exceeding its PPS capacity.

This is a key distinction:

**Bandwidth determines how much data a network can carry. PPS capacity determines how many individual packets a system can handle.**

## 5. Important distinction: wire PPS vs. kernel packet-processing rate

**On Linux, packet-processing rate is not necessarily identical to the physical packet rate.**

Modern networking optimizations include:

- GRO (Generic Receive Offload): Aggregates multiple received packets into larger packet representations for processing.
- TSO (TCP Segmentation Offload): Allows the NIC to segment a large TCP payload into multiple packets.
- GSO (Generic Segmentation Offload): Defers segmentation of large packets until later in the transmit path.
- NAPI: Processes received packets in batches rather than requiring an interrupt for every packet.

Consequently, a NIC might receive one million physical packets per second while upper layers of the kernel operate on fewer aggregated SKBs.

**The exact meaning of a PPS measurement therefore depends on where it is collected**: NIC hardware counters, interface statistics, kernel tracing, or application-level instrumentation.

## 6. The three main networking performance metrics

| Metric                 | What it measures                            | Typical unit |
| ---------------------- | ------------------------------------------- | ------------ |
| Bandwidth / throughput | Data transferred per second                 | Gbps         |
| Packet rate            | Packets transferred or processed per second | Mpps         |
| Latency                | Time required to transfer or process data   | µs           |

A networking system can have excellent bandwidth, yet poor PPS capacity for small packets.

This is particularly relevant to distributed databases, high-performance messaging systems, and packet-processing applications, where packets may be small and frequent.

The fundamental principle: **Moving 1 GB as a small number of large packets is generally less expensive in per-packet processing overhead than moving the same 1 GB as millions of small packets.**
