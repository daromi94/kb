# CPU sockets

A CPU socket is a physical connector on a motherboard that holds a processor and establishes its electrical connections to the rest of the computer.

In server hardware, the term socket also refers to a physical processor position. Consequently, a dual-socket server is a machine capable of accommodating two physical CPU packages.

## 1. What is a CPU socket?

Consider a motherboard with one CPU socket:

```text
+----------------------------------------+
|              MOTHERBOARD               |
|                                        |
|      +--------------------------+      |
|      |        CPU SOCKET        |      |
|      |                          |      |
|      |    +----------------+    |      |
|      |    |  CPU PACKAGE   |    |      |
|      |    |                |    |      |
|      |    | Core 0  Core 1 |    |      |
|      |    | Core 2  Core 3 |    |      |
|      |    | Core 4  Core 5 |    |      |
|      |    | Core 6  Core 7 |    |      |
|      |    +----------------+    |      |
|      +--------------------------+      |
|                                        |
|      RAM                 PCIe slots    |
|                                        |
+----------------------------------------+
```

There are three distinct concepts:

- Socket: The physical motherboard connector.
- Package: The physical processor assembly installed in the socket.
- Core: An independent CPU execution engine inside the processor.

A single socket can accommodate a processor containing dozens or even hundreds of cores, depending on the architecture.

Importantly, a CPU socket does not execute instructions. It provides the mechanical and electrical interface for the processor that does.

## 2. What's inside a CPU package?

A modern processor package contains considerably more than CPU cores.

A simplified server CPU architecture:

```text
CPU PACKAGE
+------------------------------------+
|                                    |
|   +--------+          +--------+   |
|   | Core 0 |          | Core 1 |   |
|   |  L1/L2 |          |  L1/L2 |   |
|   +--------+          +--------+   |
|                                    |
|   +--------+          +--------+   |
|   | Core 2 |          | Core 3 |   |
|   |  L1/L2 |          |  L1/L2 |   |
|   +--------+          +--------+   |
|                                    |
|   +----------------------------+   |
|   | Shared last-level cache    |   |
|   +----------------------------+   |
|                                    |
|   +----------------------------+   |
|   | On-package interconnect    |   |
|   +----------------------------+   |
|                                    |
|   +------------+  +------------+   |
|   | Memory     |  | PCIe / I/O |   |
|   | controller |  | interfaces |   |
|   +------------+  +------------+   |
|                                    |
+------------------------------------+
           |            |
           v            v
         DRAM          PCIe
```

This is a conceptual diagram, not a universal physical layout. Cache organization and placement differ between processors.

Modern processors may also contain multiple silicon dies or chiplets in a single package. Multiple chiplets do not necessarily mean multiple sockets.

## 3. Single-socket vs. multi-socket systems

A computer can have one or multiple physical CPU sockets.

### Single-socket system

```text
             +------------------+
             |     SOCKET 0     |
             |                  |
             |  CPU Package     |
             |  16 CPU cores    |
             |  Memory Ctrl     |
             |  PCIe Ctrl       |
             +------------------+
                |          |
                |          +---- PCIe devices
                |
          +-----+-----+
          |           |
       Memory      Memory
       Channel 0   Channel 1
          |           |
         RAM         RAM
```

All 16 cores belong to the same processor package.

### Dual-socket system

A dual-socket server contains two processor packages, typically connected through a high-speed, cache-coherent interconnect.

```text
+----------------------+    +----------------------+
|       SOCKET 0       |    |       SOCKET 1       |
|                      |    |                      |
|    +------------+    |    |    +------------+    |
|    | 16 Cores   |    |    |    | 16 Cores   |    |
|    +------------+    |    |    +------------+    |
|                      |    |                      |
|    Memory Ctrl       |    |    Memory Ctrl       |
|                      |    |                      |
+----------+-----------+    +----------+-----------+
           |                           |
           +------ Interconnect -------+
           |                           |
           v                           v
     +-----------+               +-----------+
     |  RAM 0    |               |  RAM 1    |
     +-----------+               +-----------+
```

In this example:

- 2 physical sockets
- 2 processor packages
- 16 cores per socket
- 32 physical cores total
- 64 logical CPUs if every core supports and enables two-way SMT

Each package also has its own memory-controller resources.

## 4. CPU sockets and NUMA

NUMA (Non-Uniform Memory Access) means that memory-access latency and bandwidth depend on the relationship between the requesting CPU and the memory being accessed.

Consider a dual-socket server:

```text
                   INTERCONNECT
             +---------------------+
             |                     |
       +-----+------+        +-----+------+
       |  SOCKET 0  |        |  SOCKET 1  |
       |            |        |            |
       |   Core 0   |        |   Core 16  |
       |   Core 1   |        |   Core 17  |
       |   ...      |        |   ...      |
       +-----+------+        +-----+------+
             |                     |
             |                     |
       +-----+------+        +-----+------+
       |   RAM 0    |        |   RAM 1    |
       +------------+        +------------+
```

Suppose Core 0 needs to read some data.

Case A: Local memory access

```text
Core 0
   |
   v
Memory Controller 0
   |
   v
RAM 0

Local access
```

Case B: Remote memory access

```text
Core 0
   |
   v
Socket 0 Interconnect
   |
   v
Socket 1 Interconnect
   |
   v
Memory Controller 1
   |
   v
RAM 1

Remote access
```

Remote memory access typically has greater latency, and available bandwidth may be constrained by the inter-socket connection.

This has several practical implications:

1. Operating systems benefit from scheduling threads near their allocated memory.
2. Thread migration between sockets can degrade cache locality.
3. Memory-intensive applications can suffer from excessive remote accesses.
4. Cross-socket synchronization can produce additional cache-coherence traffic.

An important detail: one CPU socket does not necessarily correspond to one NUMA node. A single socket can be divided into multiple NUMA domains, depending on CPU architecture and platform configuration.

## 5. Why have multiple sockets?

Multiple sockets provide additional hardware resources, not merely additional execution cores.

| Resource           | Potential benefit                               |
| ------------------ | ----------------------------------------------- |
| CPU cores          | Greater aggregate compute capacity              |
| Memory controllers | More aggregate memory bandwidth                 |
| Memory channels    | Higher memory capacity and bandwidth            |
| PCIe connectivity  | Additional I/O resources, depending on platform |
| Cache capacity     | More aggregate on-chip cache                    |

However, there are costs:

- Inter-socket communication latency.
- Cache-coherence overhead.
- NUMA-aware memory placement requirements.
- Higher power consumption and motherboard complexity.

A single large CPU is therefore sometimes preferable to two smaller CPUs, even when the total physical core count is identical.

## 6. How Linux represents CPU sockets

Linux exposes physical processor topology, including packages, cores, and hardware threads.

The simplest command:

```bash
lscpu
```

Example output from an illustrative dual-socket machine:

```text
Architecture:          x86_64
CPU(s):                64
Socket(s):              2
Core(s) per socket:    16
Thread(s) per core:     2
NUMA node(s):           2
```

These values mean:

```text
Physical sockets: 2
       |
       v
Physical cores:   2 x 16 = 32
       |
       v
Logical CPUs:     32 x 2 = 64
```

Linux also exposes topology information through:

```text
/sys/devices/system/cpu/cpuX/topology/
```

For example:

```bash
cat /sys/devices/system/cpu/cpu0/topology/physical_package_id
```

The result identifies the physical package associated with logical CPU 0, typically corresponding to its socket.

To examine NUMA topology:

```bash
numactl --hardware
```

This reveals NUMA nodes, their associated CPUs, available memory, and relative memory distances.

## 7. Physical socket compatibility

A socket is also an electrical and mechanical interface.

Different CPU families require particular socket designs.

Common connection technologies include:

- LGA (Land Grid Array): Contacts are on the processor package; spring contacts are typically in the motherboard socket.
- PGA (Pin Grid Array): Pins are on the processor package and fit into holes in the socket.
- BGA (Ball Grid Array): The processor package is soldered directly to the motherboard, rather than being installed in a replaceable socket.

Physical compatibility is not sufficient by itself: firmware, power delivery, electrical signaling, and platform support must also be compatible.

## Key takeaway

A CPU socket has two important meanings:

Physically: It connects a processor package to the motherboard.

Architecturally: It identifies a processor package that may contain many CPU cores, caches, memory controllers, and I/O interfaces.

In performance engineering, the most consequential distinction is often between communication within a socket and communication across sockets. This affects memory locality, cache coherence, synchronization overhead, and workload placement.
