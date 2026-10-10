# Network Interface Controller (NIC)

A Network Interface Controller (NIC) is a hardware device responsible for transmitting and receiving network traffic.

In Ethernet networks, the NIC provides the hardware interface between a computer and the network. Modern NICs do considerably more than convert bytes into electrical or optical signals: they also perform DMA transfers, manage hardware queues, classify packets, generate interrupts, and offload certain networking operations from the CPU.

The central idea:

> The NIC moves Ethernet frames between the physical network and system memory. The Linux kernel, through a device driver, coordinates the NIC and processes the packets.

Understanding NICs requires understanding the boundary between hardware, kernel drivers, memory, and the networking stack.

## 1. Where does the NIC fit?

Consider two Linux servers exchanging data over TCP.

```text
             SERVER A                         SERVER B

  +---------------------------+    +---------------------------+
  | USER SPACE                |    | USER SPACE                |
  |                           |    |                           |
  |       Application         |    |       Application         |
  |           |               |    |           ^               |
  |         send()            |    |         recv()            |
  +-----------|---------------+    +-----------|---------------+
              |                                |
  +-----------|---------------+    +-----------|---------------+
  | KERNEL SPACE              |    | KERNEL SPACE              |
  |           v               |    |           |               |
  |       TCP / IP            |    |       TCP / IP            |
  |           |               |    |           ^               |
  |           v               |    |           |               |
  |       NIC Driver          |    |       NIC Driver          |
  +-----------|---------------+    +-----------|---------------+
              |                                |
  +-----------|---------------+    +-----------|---------------+
  | HARDWARE  v               |    |           |  HARDWARE     |
  |    +-------------+        |    |    +-------------+        |
  |    |     NIC     |        |    |    |     NIC     |        |
  |    +------+------+        |    |    +------+------+        |
  +-----------|---------------+    +-----------|---------------+
              |                                |
              +----------- Ethernet -----------+
```

There are three distinct components:

| Component              | Responsibility                                                                   |
| ---------------------- | -------------------------------------------------------------------------------- |
| Linux networking stack | Implements TCP/IP, routing, socket communication, and packet processing          |
| NIC driver             | Controls hardware, configures queues, manages buffers and DMA                    |
| NIC hardware           | Sends and receives Ethernet frames, performs DMA and supported hardware offloads |

The NIC itself normally does not implement the entire TCP connection. TCP state, retransmission logic, congestion control, and socket semantics are generally maintained by Linux.

Some specialized NICs support additional transport offloads, but they are not required for ordinary networking.

## 2. What is inside a modern NIC?

A modern Ethernet NIC contains multiple hardware components.

```text
+--------------------------------------+
|                 NIC                  |
|                                      |
|  +--------------------------------+  |
|  | Ethernet MAC                   |  |
|  |                                |  |
|  | Frame handling                 |  |
|  | MAC address filtering          |  |
|  +----------------+---------------+  |
|                   |                  |
|  +----------------v---------------+  |
|  | Packet Processing              |  |
|  |                                |  |
|  | RSS / Classification           |  |
|  | Checksum / TSO offloads        |  |
|  +----------------+---------------+  |
|                   |                  |
|  +----------------v---------------+  |
|  | Queue Management               |  |
|  |                                |  |
|  | RX queues / TX queues          |  |
|  | Descriptor processing          |  |
|  +----------------+---------------+  |
|                   |                  |
|  +----------------v---------------+  |
|  | DMA Engine                     |  |
|  |                                |  |
|  | Read / Write host memory       |  |
|  +----------------+---------------+  |
|                   |                  |
|  +----------------v---------------+  |
|  | Host Interface                 |  |
|  | PCIe, for example              |  |
|  +--------------------------------+  |
|                                      |
|  Ethernet MAC <--> PHY / Transceiver |
+--------------------------------------+
```

This is a functional diagram, not a literal chip layout.

Important components include:

- MAC (Media Access Control): Handles Ethernet frame transmission and reception, including frame-level operations.
- PHY (Physical Layer): Handles electrical or optical signaling. Depending on the hardware, the PHY may be integrated or external.
- DMA engine: Transfers packet data directly between the NIC and host memory.
- RX/TX queues: Organize packet reception and transmission.
- Packet-processing hardware: Can perform filtering, hashing, checksum calculation, segmentation, and other supported offloads.
- Host interface: Connects the NIC to the CPU and memory subsystem, commonly through PCI Express.

For Linux, the two most important mechanisms to understand next are DMA and descriptor rings.

## 3. DMA: How the NIC accesses system memory

DMA stands for Direct Memory Access.

Without DMA, the CPU could theoretically move incoming packet bytes from a device register into RAM by repeatedly reading and copying them.

That would waste significant CPU time.

Instead, modern NICs use DMA to transfer packet data between the device and system memory without requiring the CPU to copy every byte.

### Conceptual comparison

Without DMA:

```text
NIC
|
| Packet bytes
v
CPU
|
| CPU copies bytes
v
RAM
```

With DMA:

```text
+------------------+
|       CPU        |
|                  |
| Configures NIC   |
+--------+---------+
         |
         | Control operations
         v
+------------------+
|       NIC        |
|                  |
|    DMA Engine    |
+--------+---------+
         |
         | Direct memory transfer
         v
+------------------+
|    System RAM    |
|                  |
|  Packet buffers  |
+------------------+
```

The CPU still performs control and packet-processing work. But it does not need to execute an instruction for every byte transferred between the NIC and RAM.

### How does the NIC know where to write?

The Linux driver prepares memory buffers and maps them using the DMA API.

For example:

```c
dma_addr_t dma_addr;

dma_addr = dma_map_single(
    device,
    buffer,
    size,
    DMA_FROM_DEVICE
);
```

This produces an address suitable for the device's DMA operations.

The driver can then supply that address to the NIC.

The address may be translated by an IOMMU (Input-Output Memory Management Unit) before the memory transaction reaches physical RAM.

```text
 NIC DMA Engine
       |
       | DMA address
       v
+-------------+
|    IOMMU    |
|  (if used)  |
+------+------+
       |
       | Physical address
       v
+-------------+
| System RAM  |
|             |
| RX buffer   |
+-------------+
```

Not every platform requires an IOMMU, and its presence does not change the general DMA programming model.

A critical distinction:

DMA avoids CPU-driven copying between the NIC and host memory. It does not automatically eliminate later copies between kernel and application memory.

## 4. Descriptor rings: How the CPU and NIC coordinate

One of the most important concepts in NIC architecture is the descriptor ring.

A descriptor ring is a circular array of entries used by the driver and NIC to coordinate packet transfers.

Each descriptor typically contains information such as:

- DMA address of a packet buffer.
- Buffer length or packet length.
- Status and control flags.

A descriptor is generally not the packet data itself. It describes where the packet data resides and how the hardware should process it.

```text
RX Descriptor Ring (in system memory)

      +----------------------+
+---->| Descriptor 0         |
|     | DMA addr -> Buffer A |
|     +----------------------+
|     | Descriptor 1         |
|     | DMA addr -> Buffer B |
|     +----------------------+
|     | Descriptor 2         |
|     | DMA addr -> Buffer C |
|     +----------------------+
|     | Descriptor 3         |
|     | DMA addr -> Buffer D |
|     +----------------------+
|                |
+----------------+
        Circular
```

The driver and NIC maintain indexes or equivalent state to track which descriptors are available, which have been processed, and which can be reused.

The NIC can process descriptors independently of the CPU, which is essential for efficient networking.

The Linux DMA documentation specifically identifies NIC descriptor rings as a common use case for coherent DMA memory.

## 5. How the NIC receives a packet (RX path)

Let's follow a single Ethernet frame arriving at a Linux server.

### Step 1: Linux prepares receive buffers

Before receiving packets, the NIC driver allocates buffers in system RAM and makes them available for DMA.

```text
SYSTEM RAM

RX descriptors          Packet buffers

+--------------+        +-------------+
| Descriptor 0 |------->| Buffer A    |
+--------------+        +-------------+
| Descriptor 1 |------->| Buffer B    |
+--------------+        +-------------+
| Descriptor 2 |------->| Buffer C    |
+--------------+        +-------------+
```

The driver publishes descriptors that tell the NIC where incoming data can be placed.

### Step 2: The NIC receives an Ethernet frame

```text
Ethernet Network
       |
       | Incoming frame
       v
+-------------+
|     PHY     |
+------+------+
       |
       v
+-------------+
| Ethernet MAC|
+------+------+
       |
       v
+-------------+
| RX Queue    |
| DMA Engine  |
+------+------+
       |
       | DMA write
       v
+-------------+
| System RAM  |
| RX Buffer   |
+-------------+
```

The NIC receives the frame, processes the relevant link-layer information, selects a receive queue, and transfers packet data into host memory.

It then records completion information indicating that the descriptor has been processed.

### Step 3: The NIC notifies Linux

How does the CPU learn that packets have arrived?

Traditionally, through an interrupt.

```text
NIC receives packet
    |
    v
DMA into RAM
    |
    v
Completion recorded
    |
    v
Interrupt
    |
    v
Linux Driver
```

Modern NICs commonly use MSI-X interrupts, which allow different hardware queues to use different interrupt vectors.

However, processing every incoming packet with a separate interrupt would be inefficient at high packet rates.

That is where NAPI becomes important.

## 6. NAPI: Interrupts combined with polling

NAPI is Linux's mechanism for efficiently processing network traffic by combining interrupt-driven notification with polling.

The basic idea is:

> Use interrupts to discover that work is available, then process multiple packets in a batch rather than interrupting the CPU for each packet.

A simplified NAPI execution path:

```text
                  NIC
                   |
                   | Packet arrives
                   v
             DMA completion
                   |
                   v
              Interrupt
                   |
                   v
         +--------------------+
         | Interrupt handler  |
         |                    |
         | Schedule NAPI      |
         +---------+----------+
                   |
                   v
         +--------------------+
         | NAPI poll          |
         |                    |
         | Process RX packets |
         | Reclaim TX work    |
         +---------+----------+
                   |
                   v
             More work?
              /       \
            Yes        No
             |          |
             v          v
        Continue     Complete NAPI
        polling      Re-enable IRQs
```

In typical configurations, NAPI polling runs in softirq context. Linux also supports threaded NAPI and busy-polling modes.

The driver generally keeps the relevant interrupt masked while its NAPI instance is scheduled, avoiding redundant interrupts.

A NAPI poll call is subject to a processing budget, helping Linux avoid spending unlimited time in one batch.

### The complete receive path

Putting the pieces together:

```text
    NETWORK
       |
       v
+-------------+
|     NIC     |
+------+------+
       |
       | DMA
       v
+-------------+
| RAM buffer  |
+------+------+
       |
   IRQ / NAPI
       |
       v
+-------------+
| NIC driver  |
+------+------+
       |
       v
+-------------+
| Linux packet|
| processing  |
| (sk_buff)   |
+------+------+
       |
       v
+-------------+
|   IP layer  |
+------+------+
       |
       v
+-------------+
|  TCP layer  |
+------+------+
       |
       v
+-------------+
| TCP socket  |
+------+------+
       |
     recv()
       |
       v
+-------------+
| Application |
+-------------+
```

This shows the conventional kernel networking path. XDP or other early packet-processing mechanisms can alter it before an `sk_buff` is created.

### Where does `sk_buff` fit?

The Linux networking stack commonly represents packets using `struct sk_buff`, often abbreviated `skb`.

```text
+-----------------------+
| struct sk_buff        |
|                       |
| Metadata              |
| Protocol information  |
| Buffer references     |
+-----------+-----------+
            |
            v
+-----------------------+
| Packet data           |
|                       |
| Ethernet / IP / TCP   |
| Payload               |
+-----------------------+
```

Importantly, `sk_buff` contains metadata and references to packet buffers. It does not necessarily contain the actual packet bytes inside the structure itself.

Modern drivers may also use Linux's `page_pool` API to efficiently recycle receive buffers instead of repeatedly allocating and freeing memory.

## 7. How the NIC transmits packets (TX path)

Transmission works in the opposite direction.

Suppose an application performs:

```c
send(fd, data, 4096, 0);
```

The simplified transmission process is:

```text
   APPLICATION
       |
     send()
       |
       v
+-------------+
| TCP / IP    |
+------+------+
       |
       v
+-------------+
| Linux TX    |
| processing  |
+------+------+
       |
       v
+-------------+
| NIC driver  |
+------+------+
       |
       | DMA descriptors
       v
+-------------+
| TX ring     |
+------+------+
       |
       v
+-------------+
| NIC DMA     |
| reads RAM   |
+------+------+
       |
       v
+-------------+
| MAC / PHY   |
+------+------+
       |
       v
    NETWORK
```

The important difference from RX:

- RX: NIC writes received packet data into system memory.
- TX: NIC reads packet data from system memory for transmission.

A typical driver maps outgoing packet buffers for DMA, populates TX descriptors, and notifies the device that more work is available.

Once transmission completes, the driver reclaims descriptors, DMA mappings, and associated packet resources.

Linux defines the `ndo_start_xmit` driver operation for handing packets to a network device.

A TX completion is not the same as a TCP acknowledgment. It indicates progress or completion at the device-transmission level, not that a remote application processed the bytes.

## 8. How modern NICs use multiple CPU cores

Modern servers may have 16, 32, 64, or more CPU cores.

A single receive queue can become a bottleneck when processing large amounts of traffic.

For this reason, modern NICs support multiple hardware queues.

### Receive Side Scaling (RSS)

RSS allows a NIC to distribute incoming network flows across multiple RX queues.

```text
                    NETWORK
                       |
                       v
                +--------------+
                |     NIC      |
                |              |
                | RSS hashing  |
                +------+-------+
                       |
          +------------+------------+
          |            |            |
          v            v            v
       +------+     +------+     +------+
       | RX 0 |     | RX 1 |     | RX 2 |
       +--+---+     +--+---+     +--+---+
          |            |            |
          v            v            v
       +------+     +------+     +------+
       |CPU 0 |     |CPU 1 |     |CPU 2 |
       +------+     +------+     +------+
          |            |            |
          +------------+------------+
                       |
                       v
              Linux Network Stack
```

A common implementation hashes fields such as:

```text
Source IP
Destination IP
Source Port
Destination Port
```

That hash helps select a receive queue.

Packets belonging to the same flow are generally directed to the same queue so their processing order can be maintained.

Different flows can be processed by different CPUs.

Linux also supports:

| Mechanism | Purpose                                                                |
| --------- | ---------------------------------------------------------------------- |
| RSS       | Hardware-based RX queue distribution                                   |
| RPS       | Software-based receive packet steering                                 |
| RFS       | Steer receive processing toward CPUs running the consuming application |
| XPS       | Select appropriate transmit queues based on CPU or RX queue mapping    |

A key distinction: RSS happens at the NIC, whereas RPS is performed in the Linux networking stack.

## 9. Hardware offloading: Making the NIC do more work

Modern NICs can perform operations that would otherwise require CPU instructions.

Examples include:

| Feature             | Description                                              |
| ------------------- | -------------------------------------------------------- |
| TX checksum offload | NIC completes supported packet checksums                 |
| RX checksum offload | NIC provides checksum validation information             |
| TSO                 | NIC segments large TCP data units into MTU-sized packets |
| RSS                 | NIC distributes received flows across hardware queues    |
| VLAN offload        | NIC handles supported VLAN tag operations                |

Two especially important concepts are TSO and GRO.

### TCP Segmentation Offload (TSO)

Without TSO, TCP segmentation is primarily done in software before transmission.

With TSO, Linux can submit a larger TCP data unit for the NIC to segment.

```text
                  LINUX
                    |
                    | Large TCP data unit
                    v
                +-------+
                |  NIC  |
                |  TSO  |
                +---+---+
                    |
           +--------+--------+
           |        |        |
           v        v        v
        +------+ +------+ +------+
        |Frame1| |Frame2| |Frame3|
        +------+ +------+ +------+
           |        |        |
           +--------+--------+
                    |
                    v
                 NETWORK
```

This reduces the CPU work needed to prepare many individual packets.

### Generic Receive Offload (GRO)

GRO works in the receive direction and is primarily a Linux software optimization, not simply a hardware feature.

Compatible received packets can be aggregated into a larger unit for processing higher in the networking stack.

```text
        Incoming frames
          |    |    |
          v    v    v
         [A]  [B]  [C]
          |    |    |
          +----+----+
               |
               v
           Linux GRO
               |
               v
         [ A + B + C ]
               |
               v
        TCP processing
```

The aggregation reduces some per-packet processing overhead.

These optimizations are particularly valuable at high packet rates.

## 10. What happens when the NIC cannot keep up?

Consider an incoming workload producing packets faster than Linux can process them.

```text
Incoming packets
      |
      v
+-----------+
|   NIC     |
+-----+-----+
      |
      v
+-----------+
| RX ring   |
|           |
|  FULL!    |
+-----+-----+
      |
      v
   Packets
   may drop
```

Possible bottlenecks include:

- RX descriptors or packet buffers being exhausted.
- CPU cores unable to process packets quickly enough.
- Interrupt and NAPI processing delays.
- Poor distribution of traffic across queues.
- Insufficient memory bandwidth or contention.
- Limitations of the NIC or PCIe connection.

Increasing the RX ring size may help absorb short traffic bursts. However, it cannot solve a sustained processing-rate deficit.

If packets arrive at 2 million packets per second but the system can sustain only 1.5 million packets per second, buffering merely delays the eventual overflow.

This is the same fundamental queueing principle found in distributed systems: when arrivals consistently exceed service capacity, a finite queue eventually fills.

### Interrupt coalescing

NICs can also coalesce interrupts instead of notifying the CPU immediately for every event.

```text
Without coalescing:

Packet -> IRQ
Packet -> IRQ
Packet -> IRQ
Packet -> IRQ


With coalescing:

Packet --+
Packet --+--> IRQ
Packet --+
Packet --+
```

This can improve throughput and CPU efficiency, at the cost of potentially increasing packet-delivery latency.

It complements NAPI: interrupt coalescing controls how frequently hardware notifies the CPU, while NAPI batches subsequent work.

## 11. Inspecting a NIC in Linux

The primary tools are `ip`, `ethtool`, and the kernel's `/proc` and `/sys` interfaces.

```bash
# List network interfaces
ip link show

# Show driver information
ethtool -i eth0

# Link speed, duplex, and other details
ethtool eth0

# Show hardware queue channels
ethtool -l eth0

# Show RX/TX ring configuration
ethtool -g eth0

# Show hardware offload features
ethtool -k eth0

# Show NIC and driver counters
ethtool -S eth0

# Show interrupt coalescing settings
ethtool -c eth0

# Show interrupt activity
cat /proc/interrupts
```

Not every command is supported by every device or driver.

An example ring configuration could be:

```text
$ ethtool -g eth0

Current hardware settings:
RX: 1024
TX: 1024
```

These values describe descriptor-ring capacities, not the byte size of a single packet buffer.

A hardware queue count is different from ring depth:

- Queue count: How many queues are available for parallel processing.
- Ring depth: How many descriptors an individual ring can accommodate.

`ethtool` provides the standard administrative interface for examining these capabilities.

## 12. The big picture

The complete networking path can now be understood as two separate flows.

```text
                  TRANSMISSION (TX)

       Application
            |
          send()
            |
            v
       TCP / IP stack
            |
            v
       NIC Driver
            |
            v
       TX Descriptors
            |
            v
       NIC DMA reads RAM
            |
            v
       Ethernet Network


                  RECEPTION (RX)

       Ethernet Network
            |
            v
       NIC
            |
            v
       NIC DMA writes RAM
            |
            v
       RX Descriptors
            |
            v
       NAPI / Driver
            |
            v
       IP / TCP stack
            |
            v
       Socket
            |
          recv()
            |
            v
       Application
```

### Essential principles

1. The NIC is not the networking stack. It handles physical transmission, DMA, queues, and supported hardware processing. Linux implements the higher-level protocols and socket semantics.
2. DMA is the foundation of efficient packet transfer. The NIC transfers data directly between the hardware and system memory without the CPU copying each byte.
3. Descriptor rings coordinate asynchronous hardware and software execution. The CPU and NIC operate independently while exchanging ownership and completion information.
4. NAPI reduces interrupt overhead through batching. The CPU can process multiple packets per polling cycle rather than requiring one interrupt per packet.
5. Multiqueue NICs enable multicore network processing. RSS distributes flows across RX queues, helping improve throughput and CPU utilization.
6. NIC throughput is not necessarily application throughput. Hardware capacity, CPU processing, socket buffering, memory bandwidth, and network protocols can all become bottlenecks.
