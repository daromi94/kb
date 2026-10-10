# Jumbo frames

Jumbo frames are Ethernet frames that carry more data than traditional Ethernet frames, typically by increasing the network interface's MTU from 1,500 bytes to around 9,000 bytes.

The primary motivation is simple:

> Transmitting fewer, larger packets can reduce packet-processing overhead and improve the efficiency of high-throughput networks.

Jumbo frames are especially relevant in data centers, storage networks, high-performance computing, and systems transferring large amounts of data.

## 1. Understanding the MTU

Before understanding jumbo frames, it is important to distinguish two concepts:

- Ethernet frame: The Layer 2 unit transmitted across an Ethernet network.
- MTU (Maximum Transmission Unit): The maximum size of the Layer 3 packet that can fit inside the Ethernet payload.

Layer 2 handles delivery across a local link. Layer 3, here IP (Internet Protocol), handles packets across networks.

For traditional Ethernet, the MTU is 1,500 bytes.

```text
Standard Ethernet frame - 1,518 bytes
+--------------+-------------------------+----------+
| Header: 14 B | IP packet: 1,500 B      | FCS: 4 B |
+--------------+-------------------------+----------+

Jumbo Ethernet frame - 9,018 bytes
+--------------+-------------------------+----------+
| Header: 14 B | IP packet: 9,000 B      | FCS: 4 B |
+--------------+-------------------------+----------+
```

FCS (Frame Check Sequence) is the Ethernet error-detection field.

## 2. Why jumbo frames exist

Consider transferring 9 MB of data between two Linux servers connected through a 10 Gbps Ethernet network.

For simplicity, assume the data is divided into maximum-sized IP packets and ignore protocol headers within each packet.

|                     | Standard MTU | Jumbo MTU   |
| ------------------- | ------------ | ----------- |
| MTU                 | 1,500 bytes  | 9,000 bytes |
| Approximate packets | 6,000        | 1,000       |
| Packets saved       | —            | ~83%        |

The amount of data remains the same. What changes is the number of packets required to transmit it.

NIC (Network Interface Card) is the network adapter. NIC descriptors tell the hardware where packet buffers are located.

Every packet can involve work such as:

1. Building packet headers.
2. Maintaining networking metadata.
3. Processing packets through the kernel networking stack.
4. Handling NIC descriptors and receive queues.
5. Performing routing, filtering, and protocol processing.

Although modern Linux and NICs batch and offload much of this work, the number of packets can still matter significantly.

### Relationship between packet size and packets per second

Consider a network carrying 10 Gbps continuously:

```text
1,500-byte packets -> approximately 833,000 packets/second
9,000-byte packets -> approximately 139,000 packets/second
```

These are simplified calculations based on IP-packet sizes, excluding Ethernet overhead.

The essential observation is that jumbo frames can reduce the number of packets processed by roughly six times for a given amount of transferred data.

This is why jumbo frames are frequently discussed in the context of Linux networking performance.

## 3. How jumbo frames work in Linux

Consider two Linux servers communicating over Ethernet.

On Server A:

```bash
# Inspect current MTU
ip link show dev eth0

# Configure jumbo frames
sudo ip link set dev eth0 mtu 9000
```

The network interface is now configured for IP packets up to 9,000 bytes, provided the hardware and driver support that MTU.

Replace `eth0` with the actual interface name.

The same configuration must be applied appropriately on Server B, and the switch must support the resulting Ethernet frame size. The command alone does not guarantee end-to-end jumbo-frame connectivity.

### TCP and the Maximum Segment Size (MSS)

TCP does not generally fill the entire MTU with application data because IP and TCP headers consume space.

For IPv4 and TCP without options:

```text
MSS = MTU - 20-byte IPv4 header - 20-byte TCP header
```

| MTU   | TCP MSS     |
| ----- | ----------- |
| 1,500 | 1,460 bytes |
| 9,000 | 8,960 bytes |

A larger MTU allows TCP to transmit larger segments on the wire when the path supports them.

## 4. What happens when the network doesn't support jumbo frames?

This is one of the most important operational considerations.

Imagine this network:

```text
Server A            Router              Server B
MTU 9000                                MTU 1500
    |                  |                    |
    +---- MTU 9000 ----+---- MTU 1500 ------+
                       ^
                  Bottleneck
```

A 9,000-byte IP packet cannot traverse the 1,500-byte link unchanged.

The behavior depends on the protocol and configuration:

- IPv4: A router may fragment a packet if fragmentation is permitted. With the Don't Fragment (DF) flag set, it must drop the oversized packet and normally return an ICMP fragmentation-needed message.
- IPv6: Routers do not fragment packets. They drop oversized packets and send an ICMPv6 Packet Too Big message.
- Path MTU Discovery (PMTUD): Allows the sender to learn the maximum IP packet size supported along a route and adjust transmission accordingly.

Importantly, Ethernet switches do not fragment jumbo frames into smaller Ethernet frames. If a switch port cannot handle their size, the frames may simply be discarded.

### Testing jumbo-frame connectivity

From a Linux server configured with MTU 9000:

```bash
ping -4 -M do -s 8972 192.168.1.20
```

Replace `192.168.1.20` with the destination's address. The `-4` flag selects IPv4, and `-s` specifies the number of ICMP payload bytes.

Why 8,972 bytes?

```text
9,000 bytes  MTU
  -20 bytes  IPv4 header
   -8 bytes  ICMP header
--------------------------
8,972 bytes  ICMP payload
```

`-M do` requests IPv4 PMTU handling that prohibits fragmentation. A successful reply indicates that the tested ICMP packet size worked in both directions for that exchange.

The reply may be fragmented. Run a probe from Server B to Server A to check the reverse path without fragmentation.

Another useful diagnostic is:

```bash
tracepath 192.168.1.20
```

It can help identify the path MTU.

## 5. Jumbo frames versus Linux network offloading

A particularly important distinction for Linux performance engineering:

Jumbo frames and TCP Segmentation Offload (TSO) solve different problems.

With TSO, Linux can hand a large TCP buffer to the NIC, which then divides it into smaller packets that respect the MTU.

```text
TSO with a standard 1,500-byte MTU

Large TCP buffer (~64 KB)
             |
NIC performs segmentation
             |
[TCP 1] [TCP 2] [TCP 3] [TCP 4] [TCP 5] ...
             |
Multiple standard-sized Ethernet frames are transmitted
```

Linux supports several related mechanisms. GSO means Generic Segmentation Offload, and GRO means Generic Receive Offload:

| Mechanism    | Purpose                                                |
| ------------ | ------------------------------------------------------ |
| Jumbo frames | Permit larger actual Ethernet frames                   |
| TSO          | NIC segments large TCP buffers                         |
| GSO          | Software-managed segmentation                          |
| GRO          | Combine received packets for more efficient processing |

TSO and GRO already reduce some of the CPU costs associated with smaller packets. As a result, jumbo frames may offer less improvement than expected on modern servers.

## 6. Tradeoffs and when to use them

| Advantages                         | Disadvantages                                                 |
| ---------------------------------- | ------------------------------------------------------------- |
| Fewer packets per transferred byte | Requires compatible network infrastructure                    |
| Less packet-processing overhead    | Larger frames occupy links longer                             |
| Potential CPU efficiency gains     | MTU mismatches cause difficult failures                       |
| Useful for bulk data transfers     | Can increase buffering pressure and latency for other traffic |

For example, serializing 9,000 bytes takes approximately 72 microseconds on a 1 Gbps link, compared with 12 microseconds for 1,500 bytes. Larger frames may increase head-of-line delays for other packets.

Jumbo frames tend to make sense in controlled environments such as storage networks, dedicated high-throughput data center fabrics, and high-performance computing clusters. They should not be enabled indiscriminately across arbitrary Internet-facing network paths.

A sound approach is to benchmark throughput, CPU consumption, packet rates, tail latency, and drops before and after enabling them.

## 7. Key engineering lessons

Three principles are worth retaining:

1. Path MTU is a property of a network path, not just a host interface. A large local MTU is insufficient if an intermediate link cannot carry the packets.
2. Packet rate matters independently of bandwidth. Two networks transmitting the same number of bytes per second can impose very different packet-processing loads.
3. Reducing processing overhead is not equivalent to reducing latency. Larger frames improve batching efficiency but may increase transmission delay, buffering, and the cost of packet loss.

The central principle: Jumbo frames exchange larger units of network transmission for fewer packets. Their value depends on whether packet-processing overhead is actually a bottleneck.
