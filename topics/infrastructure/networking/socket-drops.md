# Socket drops

A socket drop occurs when the kernel discards an incoming packet associated with a socket instead of successfully delivering it through the normal receive path.

Common reasons include insufficient buffer space, memory pressure, invalid packets, and overloaded packet-processing paths.

However, there is an important distinction:

> Not every packet drop is a socket drop, and not every packet drop causes application-level data loss.

For example, a packet can be dropped by the NIC before Linux even identifies which socket should receive it.

Furthermore, TCP and UDP behave very differently when packets are discarded.

## 1. Where can a packet be dropped?

Consider the Linux receive path.

```text
                     NETWORK
                        |
                        v
              +-------------------+
              | NIC               |
              |                   |
              | Hardware RX ring  |
              +---------+---------+
                        |
                        |  DROP A
                        |  No available RX buffer
                        v
              +-------------------+
              | Linux Driver      |
              | NAPI              |
              +---------+---------+
                        |
                        |  DROP B
                        |  Processing backlog full
                        v
              +-------------------+
              | Network Stack     |
              |                   |
              | IP / TCP / UDP    |
              +---------+---------+
                        |
                        |  DROP C
                        |  Invalid packet,
                        |  filtering, etc.
                        v
              +-------------------+
              | Socket Receive    |
              | Queue             |
              |                   |
              | [A] [B] [C]       |
              +---------+---------+
                        |
                        |  DROP D
                        |  Insufficient socket
                        |  buffer capacity
                        v
                      recv()
                        |
                        v
                  Application
```

Conceptual pipeline. DROP D actually occurs when the kernel attempts to admit data into socket receive state, before `recv()` reads it.

The distinction between these locations is fundamental.

| Drop location             | Example cause                              | Typical diagnostic           |
| ------------------------- | ------------------------------------------ | ---------------------------- |
| NIC hardware              | RX buffers unavailable                     | `ethtool -S`                 |
| Kernel RX processing      | Software backlog overload                  | `/proc/net/softnet_stat`     |
| IP / transport processing | Invalid packet, filtering, memory pressure | `nstat`, packet-drop tracing |
| Socket receive path       | Buffer or socket backlog exhaustion        | `ss -m`, protocol counters   |
| TCP listening socket      | Accept queue full                          | `TcpExtListenOverflows`      |

Linux explicitly distinguishes hardware receive drops, network-device drops, and protocol-level discards in its networking statistics.

## 2. Why socket receive drops happen

Consider an application receiving UDP datagrams.

The network delivers 100,000 datagrams per second, but the application can process only 60,000 per second.

```text
                 Network
              100,000 pkt/s
                    |
                    v
          +---------------------+
          | Socket RX Buffer    |
          |                     |
          |   [1] [2] [3] [4]   |
          |   [5] [6] [7] [8]   |
          |                     |
          |        FULL         |
          +----------+----------+
                     |
                     | recvfrom()
                     v
                 Application
                60,000 pkt/s
```

There is a persistent difference of 40,000 datagrams per second.

Initially, the receive buffer absorbs that excess traffic.

Eventually, the buffer becomes full.

Once Linux cannot admit another datagram, it may discard it.

### Why not just allocate more memory?

Because kernel memory is finite.

Imagine 100,000 connections, each requiring up to 1 MB of receive buffering.

The system could potentially have roughly 100 GB of receive-buffer capacity to account for, even before considering TCP state, packet metadata, send buffers, or application memory.

Linux therefore imposes socket memory limits and supports memory accounting.

The `SO_RCVBUF` socket option controls receive buffer capacity, subject to Linux's accounting conventions. It does not promise that every incoming packet will be accepted.

### Queueing explains the problem

Let:

- `lambda` = packet arrival rate.
- `mu` = packet consumption rate.
- `B` = available receive buffering capacity.

When:

```text
lambda > mu
```

the backlog grows until it reaches a capacity limit.

Increasing `B` allows longer bursts to be absorbed, but cannot solve sustained overload.

A larger buffer postpones drops; it does not increase the application's processing capacity.

## 3. TCP drops: Why they don't necessarily lose application data

TCP provides reliable, ordered byte-stream delivery.

If a TCP segment gets dropped because Linux cannot accept it, that does not automatically mean the application loses its contents.

Consider:

```text
TCP SENDER                 TCP RECEIVER

    |                          |
    | ---- Segment A --------> | Accepted
    |                          |
    | ---- Segment B --------> | Accepted
    |                          |
    | ---- Segment C --------> X DROPPED
    |                          |
    |                          |
    |   No ACK for C's bytes   |
    |                          |
    | ---- Retransmit C -----> | Accepted
    |                          |
    | <------- ACK ----------- |
```

This is simplified: retransmission may be triggered by a timer or TCP loss-detection mechanisms, and acknowledgments are cumulative.

TCP retransmission can recover the dropped data.

### But why would TCP drop data if it has flow control?

TCP advertises a receive window (`rwnd`) to constrain how much data a peer may send.

```text
                TCP RECEIVER

      +-----------------------------+
      | TCP receive buffer          |
      |                             |
      | [ Used: 48 KB ][ Free: 16K] |
      +-----------------------------+
                     |
                     v
             Advertise window
                  ~16 KB
                     |
                     v
                 TCP SENDER
```

As the receive capacity decreases, the advertised window can shrink toward zero.

Normally, this prevents sustained receiver-buffer overload.

However, drops can still occur because:

- Packets already in flight can arrive while the window is changing.
- Receive-buffer memory accounting is not equivalent to advertised byte-window space.
- Out-of-order data and packet metadata consume memory.
- The system can experience memory-allocation pressure.
- TCP may receive packets outside the currently acceptable receive window.

### TCP reliability has a cost

Even if retransmission succeeds, the drop can increase latency.

```text
Normal transmission

Packet ------------------------> Receiver
       One transmission


Transmission with drop

Packet ------------------------> X
       Loss detected

Retransmit --------------------> Receiver
```

Potential consequences include increased tail latency, retransmission traffic, and reduced throughput.

If the loss is interpreted as congestion, TCP's congestion-control algorithm may also reduce its sending rate.

TCP retransmission protects data delivery, not latency. If the connection fails before recovery, delivery is not guaranteed.

## 4. UDP drops: Where application messages disappear

UDP is different because it does not provide built-in retransmission or receiver-window flow control.

Consider three datagrams:

```text
UDP SENDER                  UDP RECEIVER

    |                           |
    | ----- Datagram A -------> | Accepted
    |                           |
    | ----- Datagram B -------> X DROPPED
    |                           |
    | ----- Datagram C -------> | Accepted
    |                           |
```

The receiving application might observe:

```text
recvfrom() -> Datagram A
recvfrom() -> Datagram C
```

Datagram B is missing.

UDP itself does not automatically recover it.

If an application requires reliable delivery over UDP, it needs an additional protocol mechanism, such as acknowledgments, retransmission, sequencing, or forward error correction.

This is a major reason UDP receive-buffer drops matter in telemetry pipelines, real-time streaming systems, and high-throughput datagram services.

## 5. TCP listening socket drops

There is another important class of drops unrelated to established socket receive buffers.

A listening TCP socket maintains a queue of established connections waiting for `accept()`.

```text
    INCOMING CLIENTS
            |
            v
    TCP handshakes
            |
            v
+-----------------------+
| TCP Accept Queue      |
|                       |
| [C1] [C2] [C3] [C4]   |
|                       |
|         FULL          |
+-----------+-----------+
            |
            | accept()
            v
        Application

Additional connections arrive
            |
            v
    Overflow handling
```

Suppose the server's accept queue has reached its configured limit.

Additional connection attempts can experience ignored packets, retransmissions, delayed connection establishment, or failures, depending on kernel behavior and configuration.

The kernel maintains counters including:

- `TcpExtListenOverflows`: Events involving listening queue overflow.
- `TcpExtListenDrops`: Packets dropped while processing a listening TCP socket; this can include overflow and other failures.

Linux distinguishes the established-connection accept queue from the queue for incomplete TCP handshakes. The `listen()` backlog governs the former, subject to `somaxconn`.

This leads to two very different diagnoses:

```text
     Slow recv()                      Slow accept()
         |                                 |
         v                                 v
  Connected socket RX               Listening socket
  data accumulates                  connections accumulate
         |                                 |
         v                                 v
  Receive-side pressure             Accept queue overflow
```

A server might accept connections quickly but read data slowly, or read established connections efficiently but accept new connections too slowly. These are separate bottlenecks.

## 6. How Linux records socket drops

Linux exposes several useful counters, but they measure different layers.

### Per-socket drop accounting

Linux maintains a socket-level drop counter, `sk_drops`, for certain packet-drop paths.

It can be inspected through `ss`:

```bash
ss -unm
```

An illustrative result:

```text
UNCONN  0  0  0.0.0.0:9000  0.0.0.0:*
        skmem:(r0,rb212992,t0,tb212992,f0,w0,o0,bl0,d125)
```

Important fields:

- `r`: Receive memory currently allocated.
- `rb`: Receive buffer accounting limit.
- `bl`: Socket backlog memory accounting.
- `d`: Socket drop counter.

Here `d125` means 125 drops have been recorded in that socket's accounting. It does not represent every loss anywhere along the network path.

### SO_RXQ_OVFL

Linux also provides the `SO_RXQ_OVFL` socket option.

When enabled, it can attach ancillary information to received packets containing the number of packets dropped by that socket since creation.

For example:

```c
int enabled = 1;

setsockopt(
    fd,
    SOL_SOCKET,
    SO_RXQ_OVFL,
    &enabled,
    sizeof(enabled)
);
```

An application retrieves the associated drop count through `recvmsg()` control messages.

This can be particularly useful for high-throughput UDP applications that need to observe local receiver overload.

## 7. Diagnosing drops in Linux

A useful investigation starts at the NIC and moves up toward the application.

```text
                  PACKET LOSS OBSERVED
                          |
                          v
                 NIC drop counters?
                    /           \
                  Yes            No
                   |              |
                   v              v
             NIC / Driver     Kernel RX path
                                  |
                                  v
                          Protocol drops?
                             /       \
                           Yes        No
                            |          |
                            v          v
                       TCP / UDP     Other causes
                            |
                            v
                      Socket metrics
                            |
                            v
                     Application rate
```

### Step 1 — Check hardware drops

```bash
ip -s -s link show dev eth0
ethtool -S eth0
```

Look for counters associated with RX missed packets, buffer exhaustion, and receive errors.

Counter names differ by NIC and driver, so their precise meanings must be checked rather than assuming every field named `drop` has the same semantics.

### Step 2 — Inspect kernel receive processing

```bash
cat /proc/net/softnet_stat
```

This displays per-CPU counters as hexadecimal values.

In the conventional layout, the first three columns represent packets processed, packets dropped, and NAPI processing cycles that exhausted their budget or time allowance.

Increasing drops here suggest processing pressure before packets reach their destination sockets.

### Step 3 — Inspect TCP and UDP counters

```bash
nstat -az | grep -E 'TCPRcvQDrop|TCPBacklogDrop|TCPZeroWindowDrop|ListenDrops|ListenOverflows|UdpRcvbufErrors|UdpInErrors'
```

Selected counters to investigate:

| Counter                   | What it suggests                                              |
| ------------------------- | ------------------------------------------------------------- |
| `TcpExtTCPRcvQDrop`       | TCP receive-queue memory pressure                             |
| `TcpExtTCPBacklogDrop`    | TCP per-socket backlog drops                                  |
| `TcpExtTCPZeroWindowDrop` | TCP segment dropped in a zero-window situation                |
| `TcpExtListenOverflows`   | TCP listening queue overflow                                  |
| `TcpExtListenDrops`       | Drops during listening socket processing                      |
| `UdpRcvbufErrors`         | UDP receive-buffer admission failures                         |
| `UdpInErrors`             | Broader UDP receive errors, including buffer-related failures |

These counters are not always independent; one event can increment multiple counters. They should be evaluated as changes over time, and their availability and exact paths can vary by kernel version.

### Step 4 — Inspect individual socket queues

```bash
ss -tnm
ss -unm
ss -lnt
```

For TCP, a consistently growing `Recv-Q` can indicate that an application is not consuming incoming data quickly enough.

For listening sockets, a `Recv-Q` approaching `Send-Q` indicates that the accept queue is near its configured capacity.

Neither observation alone proves that drops have occurred.

### Step 5 — Trace actual kernel packet drops

For more advanced investigations, Linux exposes packet-drop reasons through tracing facilities.

For example, packet-freeing paths can report an `skb_drop_reason` through the `skb:kfree_skb` tracepoint.

Tools such as `bpftrace`, `perf`, and eBPF-based networking diagnostics can help identify where drops occur. Not every packet free is a drop, so reason-aware tracing is important.

## 8. How to prevent socket drops

The correct solution depends on the location of the bottleneck.

| Problem                                 | Potential improvements                                          |
| --------------------------------------- | --------------------------------------------------------------- |
| UDP application reads too slowly        | Drain sockets in batches, optimize handlers, distribute traffic |
| UDP receive buffer too small            | Evaluate `SO_RCVBUF` and available memory                       |
| TCP accept queue overflows              | Accept connections faster, examine backlog sizing               |
| NIC RX ring exhaustion                  | Improve CPU/IRQ distribution, evaluate ring depth               |
| NAPI processing overload                | Examine CPU saturation, RSS, queue distribution                 |
| Sustained arrival rate exceeds capacity | Admission control, load shedding, or upstream rate limiting     |

Increasing every buffer is generally a poor default.

Consider:

```text
             SMALL BUFFER

   Incoming traffic ---> [Queue] ---> Consumer
                            |
                            X Drops during burst


             LARGE BUFFER

   Incoming traffic ---> [........Queue........]
                                    |
                                    v
                            Longer queue delay
                                    |
                                    v
                                 Consumer
```

A larger buffer can absorb a temporary burst, but it also permits more work to accumulate.

If the consumer remains slower than the producer, the system eventually encounters the same problem, potentially with greater memory usage and latency.

For TCP, larger buffers can also interact with receive-window sizing and throughput. Linux provides automatic TCP receive-buffer tuning for this reason.

## 9. A distributed-systems perspective

Socket drops are a practical manifestation of finite resource capacity.

The sequence is:

```text
Incoming workload
    |
    v
Finite queue
    |
    v
Processing capacity
    |
    v
Application
```

When the workload exceeds the processing capacity, one of four things must happen: the producer slows down, the backlog grows, excess work is dropped, or additional processing capacity becomes available.

TCP has built-in flow control to constrain the producer, while UDP leaves much more responsibility to the application protocol.

This creates a crucial distinction between three concepts:

Buffering absorbs temporary differences between arrival and processing rates.

Backpressure communicates that downstream capacity is constrained so upstream production can slow down.

Load shedding deliberately rejects or discards work to protect system stability.

Socket drops can be an unintended form of load shedding. Unlike deliberate application-level rejection, they often provide little context to the sender about why work disappeared.

## 10. Final mental model

```text
                   INCOMING TRAFFIC
                          |
                          v
                   +-------------+
                   | NIC RX Ring |
                   +------+------+
                          |
                          v
                   +-------------+
                   | NAPI / IP   |
                   +------+------+
                          |
                          v
                +-------------------+
                | TCP or UDP Socket |
                | Receive Buffer    |
                +---------+---------+
                          |
                    Full buffer?
                     /       \
                   No         Yes
                    |          |
                    v          v
                 Accept     TCP: Flow control /
                 data       possible packet drop
                    |          |
                    |          +--> Retransmission
                    |               may recover data
                    |
                    |        UDP: Datagram drop
                    |               |
                    |               +--> No built-in
                    |                    retransmission
                    v
                 recv()
                    |
                    v
                Application
```

The most important lesson: Socket drops are not necessarily evidence that the network is unreliable. They can indicate that the Linux host or application cannot process incoming traffic quickly enough.

And for diagnosing performance, the first question should always be: Is traffic being dropped at the NIC, inside the kernel networking stack, at socket admission, or during connection establishment?
