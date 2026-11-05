# TCP complexity

TCP is expensive because it provides a strong set of guarantees over a network that is fundamentally unreliable.

Its primary design goal is not to minimize CPU cycles, memory accesses, or latency. It is to provide a reliable, ordered byte stream between two processes, regardless of the underlying network's behavior.

That distinction explains most of TCP's complexity.

## 1. The fundamental problem TCP was designed to solve

The Internet Protocol (IP) provides a best-effort datagram service. IP does not guarantee that packets will arrive, arrive only once, or arrive in their original order.

Consider an application sending three pieces of data:

```text
Sender                                  Receiver

[ A ] --------------------------------> [ A ]

[ B ] --------------- X                 Lost

[ C ] --------------------------------> [ C ]

Receiver observes: A, C
```

Several things can go wrong:

- A packet can disappear because a router's queue overflows.
- A packet can arrive after a later packet.
- A packet can be duplicated.
- A packet can be corrupted.
- The receiver can process data more slowly than the sender transmits it.
- The network can become congested when many senders compete for the same resources.

TCP was designed to hide these problems from applications.

Instead of exposing packet delivery directly, TCP provides an abstraction:

```text
Application A                           Application B
    |                                       ^
    | write("ABC")                          | read()
    v                                       |
+-------+                               +-------+
|  TCP  |                               |  TCP  |
+-------+                               +-------+
    |                                       ^
    |                                       |
    +-------- Unreliable IP network --------+

Application B sees: "ABC"
```

If data is lost, TCP attempts to recover it. If segments arrive out of order, TCP reconstructs the original stream before exposing it to the application.

TCP must operate over a potentially unreliable datagram service, across many different types of networks.

**The fundamental tradeoff: TCP makes networking easier and safer for applications by moving substantial complexity into the transport layer.**

## 2. The assumptions behind TCP

TCP's architecture becomes easier to understand by examining the assumptions under which it operates.

| Assumption                                        | Design consequence                      |
| ------------------------------------------------- | --------------------------------------- |
| Packets can be lost                               | ACKs, loss detection, retransmission    |
| Packets can arrive out of order                   | Sequence numbers, reassembly buffers    |
| Packets can be duplicated                         | Duplicate detection                     |
| Network capacity is initially unknown             | Congestion control, pacing, probing     |
| Receivers have finite memory                      | Flow control                            |
| Network paths and conditions can change           | Adaptive RTT and congestion estimates   |
| Different machines and networks must interoperate | Standardized protocol and state machine |
| Applications often want a continuous stream       | In-order byte-stream semantics          |

These assumptions aren't arbitrary. They follow from the original objective: to connect heterogeneous networks without requiring every intermediate network to offer reliable transport.

### The historical distinction

There are two major stages in TCP's evolution.

1970s-1981: Reliability and internetworking. TCP emerged from the work of Vint Cerf and Bob Kahn. The 1981 specification formalized connection establishment, sequencing, acknowledgments, retransmission, and flow control.

Mid-to-late 1980s: Preventing congestion collapse. The growing Internet exposed a further problem: even when endpoints were behaving correctly from a reliability perspective, excessive transmission and retransmission could overwhelm the network.

Van Jacobson's 1988 paper, Congestion Avoidance and Control, documented the problem and described algorithms that became foundational to TCP congestion control.

Congestion control was therefore an important later evolution of TCP, not simply one inseparable part of the original 1981 design.

This history matters because TCP carries the costs of solving two different problems:

1. Deliver bytes reliably and in order.
2. Prevent the transport from overwhelming a shared network.

Those objectives create different performance costs.

## 3. What actually makes TCP expensive?

There are several independent costs. Some come directly from TCP's semantics; others come from how Linux implements the networking stack.

### 3.1. Reliability requires keeping data and tracking acknowledgments

Imagine sending 8 KiB through an established TCP connection.

TCP cannot simply discard the data after transmitting it. Until the receiver acknowledges it, the sender must retain the ability to retransmit it.

```text
TCP sender

Application
    |
    | write(8 KiB)
    v
+-----------------------------------+
| TCP send / retransmission state   |
|                                   |
| Data not yet acknowledged         |
|                                   |
| [ S1 ][ S2 ][ S3 ][ S4 ] ...      |
+-----------------------------------+
    |
    | Transmit segments
    v
Network ------------------------------> Receiver
                                            |
    +----------------- ACK -----------------+
    |
    v
TCP processes ACK
Advances acknowledged sequence
Releases acknowledged data/state
Updates congestion and RTT information
```

The sender needs to maintain sequence numbers, information about outstanding data, retransmission state, and RTT measurements.

This generates several costs:

- **Memory:** Outstanding data must remain available for retransmission, along with bookkeeping structures.
- **CPU:** ACK processing updates transport state, determines which bytes are acknowledged, and may update congestion-control or loss-recovery information.
- **Cache:** Connection state, packet metadata, and buffering structures consume cache capacity and memory bandwidth.
- **Network:** ACKs consume some reverse-path bandwidth and processing capacity.

Importantly, TCP does not wait for an ACK after every segment before sending the next one. It uses sliding windows that permit multiple segments to remain in flight simultaneously. ACKs may acknowledge multiple segments at once.

Also, **an application's successful `send()` call does not mean the remote application has received the data.** Usually, it means the local kernel accepted the data for transmission.

### 3.2. Ordered delivery introduces head-of-line blocking

This is one of TCP's most consequential semantic costs.

Consider three TCP segments carrying consecutive ranges of the byte stream:

```text
Sender                                  Receiver

S1 -----------------------------------> S1 arrived

S2 --------------- X                    S2 lost

S3 -----------------------------------> S3 arrived

Receiver's TCP state:

[ S1 ][ missing S2 ][ S3 received ]
   |
   v
Deliver S1
Cannot deliver S3 as subsequent stream bytes
Wait for S2
```

**Even though S3 has arrived, the receiver cannot expose the bytes after the missing gap through the ordinary TCP stream interface.**

TCP must first reconstruct the contiguous byte sequence.

This is head-of-line blocking.

Why was it designed this way? Because applications such as remote terminals and file transfers needed a reliable, ordered sequence of bytes. Delivering bytes out of order would violate that abstraction.

But for a distributed query engine or message-passing workload, this guarantee may be unnecessarily restrictive.

Suppose S2 and S3 belong to independent logical messages. In a message-oriented transport that permits independent delivery, S3 might be processed immediately despite the loss of S2.

TCP's ordering requirement prevents that on the same connection.

Loss recovery adds further latency: the sender must detect the loss and retransmit the missing data. Modern mechanisms such as RACK-TLP reduce recovery delays, but do not eliminate in-order delivery constraints.

### 3.3. Congestion control adds feedback loops

TCP must avoid overwhelming a network whose capacity it does not necessarily know.

It maintains two conceptually separate limits:

- `rwnd`: How much data the receiver is willing to accept.
- `cwnd`: How much outstanding data the sender's congestion-control algorithm permits.

The effective flight-size limit is constrained by both:

```text
Outstanding data <~ min(cwnd, rwnd)
```

Consider:

```text
Sender

Application has 1 MiB available
      |
      v
+-----------+
| TCP       |
|           |
| cwnd      |  Limits network usage
| rwnd      |  Limits receiver usage
+-----------+
      |
      | Allowed transmission
      v
Shared network
      |
      v
  Receiver
      |
      | ACK feedback
      v
Sender updates state
```

**A sender cannot assume that a fast local NIC means the entire path has unlimited capacity.**

The connection could traverse a slow link, a congested router, or a receiver whose application stops reading.

TCP therefore estimates network conditions and adjusts transmission behavior.

This can introduce a performance cost through conservative sending and loss recovery, especially during startup, after idle periods, or when congestion signals appear.

However, on a healthy, short-RTT connection with a sufficiently large congestion window, this need not add a round-trip delay to each application message.

Congestion-control algorithms are fundamentally a compromise between utilization, latency, stability, and fairness.

### 3.4. Linux's kernel networking path consumes CPU cycles

This is especially important for low-latency communication between machines in a data center.

Even if no packets are lost, no retransmissions occur, and congestion control is not limiting transmission, Linux must still move data through its networking subsystem.

A simplified TCP data path:

```text
Sender host                             Receiver host

+------------------+                    +------------------+
| Application      |                    | Application      |
+------------------+                    +------------------+
         |                                       ^
         | send()                                | recv()
         v                                       |
+------------------+                    +------------------+
| Kernel           |                    | Kernel           |
|                  |                    |                  |
| Copy / map data  |                    | Socket buffers   |
| TCP state        |                    | TCP processing   |
| Socket buffers   |                    | Sequence checks  |
| Segment handling |                    | ACK generation   |
| IP processing    |                    | IP processing    |
+------------------+                    +------------------+
         |                                       ^
         v                                       |
+------------------+                    +------------------+
| NIC driver       |                    | NIC driver       |
| TX queue         |                    | RX queue / NAPI  |
+------------------+                    +------------------+
         |                                       ^
         v                                       |
        NIC ------------- Network ------------- NIC
```

Several operations can contribute to latency and CPU consumption.

System calls and context boundaries. Ordinary socket I/O enters the kernel. This incurs entry/exit overhead, although a system call does not necessarily cause a context switch to another thread.

Memory copies. Ordinary buffered socket transmission typically copies application bytes into kernel-managed storage. Reception commonly copies bytes back into application memory. These copies also consume memory bandwidth.

Packet metadata. Linux manages packet structures such as `sk_buff`, socket queues, and related metadata.

Receive processing. NIC interrupts, NAPI polling, protocol handling, and eventual application wakeups require CPU work. Interrupt coalescing and scheduling may add latency.

Cache locality. Packet processing and application processing may run on different CPUs. Moving data and metadata between cache domains can be expensive.

Crucially, these are not exclusively TCP costs. Standard Linux UDP sockets use much of the same kernel networking infrastructure.

**Removing TCP's reliability mechanisms while retaining ordinary UDP sockets does not automatically eliminate system calls, kernel packet processing, or memory copies.**

### 3.5. Connection management and transport state

TCP is connection-oriented.

A normal new connection requires a three-way handshake:

```text
Client                                  Server

  |                                       |
  | --------------- SYN ----------------> |
  |                                       |
  | <------------ SYN + ACK ------------- |
  |                                       |
  | --------------- ACK ----------------> |
  |                                       |
  |        Connection established         |
```

This normally introduces one RTT before the connection is established, although techniques such as TCP Fast Open can change startup behavior.

Each established connection also has state associated with sequencing, buffering, windows, congestion control, recovery, and lifecycle management.

Why? The endpoints must agree on the connection's initial sequence-number spaces and distinguish new data from potentially delayed segments belonging to previous connection instances.

**For long-lived connections, handshake cost is amortized and often insignificant.** For workloads that repeatedly create short-lived connections, it can become important.

### 3.6. Latency-oriented traffic conflicts with batching optimizations

TCP implementations also try to avoid transmitting excessive numbers of small packets.

The Nagle algorithm, for example, can postpone the transmission of small writes while earlier data is unacknowledged.

The reason is historical and practical: a one-byte application write should not necessarily generate a full network packet with tens of bytes of headers.

That improves network efficiency but can hurt interactive latency.

Linux supports `TCP_NODELAY` to disable Nagle's algorithm. Separately, delayed acknowledgments can affect timing and interact poorly with applications that make a series of small dependent writes.

This is an example of a recurring tradeoff:

**Optimizing network efficiency sometimes conflicts with optimizing the latency of individual application writes.**

## 4. Are these costs still relevant on modern Linux?

They are, but TCP has undergone enormous optimization.

Modern implementations do not necessarily process every physical network segment independently at every stage.

| Optimization          | What it reduces                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------- |
| TSO                   | CPU work for segmenting large TCP writes, using supported NIC hardware.                   |
| GSO                   | Repeated processing of individual segments until software segmentation becomes necessary. |
| GRO                   | Receive-side processing overhead by aggregating packets.                                  |
| Checksum offload      | CPU time spent calculating or verifying checksums.                                        |
| Zero-copy interfaces  | Some user/kernel payload copying, subject to hardware and API constraints.                |
| NAPI and busy polling | Interrupt overhead or wakeup latency through polling and batching tradeoffs.              |

`MSG_ZEROCOPY` has its own overhead and is generally more beneficial for larger writes, historically around 10 KiB or more.

For an 8 KiB message, this matters: the payload may span several wire packets while still being processed efficiently as a larger unit in parts of the stack.

Consequently, **TCP's actual overhead cannot be estimated simply by counting packets and multiplying by the cost of a fully independent protocol-stack traversal.**

## 5. TCP versus UDP: which costs disappear?

| Property                | TCP               | Ordinary UDP                   |
| ----------------------- | ----------------- | ------------------------------ |
| Reliable delivery       | Built in          | Not provided                   |
| Ordered byte stream     | Built in          | Not provided                   |
| Retransmissions         | Built in          | Not provided                   |
| ACK processing          | Built in          | Application/protocol dependent |
| Congestion control      | Built in          | Not inherently provided        |
| Receiver flow control   | Built in          | Not inherently provided        |
| Connection handshake    | Normally required | Not required                   |
| Kernel networking stack | Yes               | Yes                            |
| Kernel memory copies    | Common            | Common                         |
| NIC/driver processing   | Yes               | Yes                            |

UDP is simpler because it deliberately does less.

But a reliable transport implemented over UDP, such as Aeron, must still perform sequencing, loss detection, retransmission, and flow-control work to provide its own guarantees.

The distinction is that a specialized protocol can choose different semantics and implementations.

For example, it may avoid TCP's single ordered byte-stream abstraction, use preallocated buffers, poll actively, or expose received data through shared-memory structures.

Those choices can improve latency and predictability for certain workloads, although they introduce their own costs.

## 6. What if the network is extremely reliable?

Consider two machines communicating across a well-provisioned data-center network.

Assume that the connections are persistent, packet loss is rare, RTT is low, and offered traffic stays below available capacity.

Under these conditions, most TCP retransmission and congestion-recovery machinery remains relatively inactive.

The interesting costs become different:

Illustrative hot path for a short message

```text
Application writes
        |
        v
Socket/kernel processing
        |
        v
Data transfer into NIC
        |
        v
Network transit
        |
        v
NIC receive processing
        |
        v
TCP receive processing
        |
        v
Application reads
```

Depending on the setup, CPU processing, memory movement, batching, and thread wakeups may dominate the overhead beyond physical network transit.

This explains why high-performance messaging systems frequently focus on removing kernel crossings, reducing copies, reusing memory, improving CPU affinity, and avoiding scheduler wakeup variability.

In such an environment, TCP's most expensive aspect is not necessarily its congestion-control arithmetic or ACK processing.

It can be the general-purpose operating-system networking architecture through which TCP is ordinarily implemented.

There is an important distinction, however: a user-space TCP implementation or specialized zero-copy TCP path can reduce some of this implementation overhead without abandoning TCP's protocol semantics.

## 7. Why not design TCP specifically for reliable data-center networks?

Because the Internet was not designed around a single type of network.

The architectural decision was to keep the network relatively general and place end-to-end communication intelligence at the endpoints.

```text
Internet architecture

+-------------+                 +-------------+
| Endpoint A  |                 | Endpoint B  |
|             |                 |             |
| TCP state   |                 | TCP state   |
| Reliability |                 | Reliability |
| Ordering    |                 | Ordering    |
+-------------+                 +-------------+
       |                               ^
       v                               |
   +--------+      +--------+      +--------+
   | Router | ---> | Router | ---> | Router |
   +--------+      +--------+      +--------+

Forward datagrams without needing
each TCP connection's full state
```

This architecture allows TCP to operate across widely varying underlying communication technologies.

End-to-end state should generally remain at endpoints rather than requiring every intermediate router to maintain it.

That is an exceptionally valuable property for a global network.

For a narrowly controlled cluster with predictable latency, however, some of TCP's generality may be unnecessary.

## 8. The essential distinction: protocol costs versus implementation costs

| Category             | Examples                                            | Can it be avoided?                                      |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| Semantic costs       | Strict ordering, loss recovery, reliable delivery   | Only by changing guarantees                             |
| Control costs        | ACKs, congestion control, flow control              | By changing the transport/control model, with tradeoffs |
| Implementation costs | System calls, copies, packet metadata, cache misses | Often reducible through optimization or kernel bypass   |
| Environmental costs  | RTT, congestion, packet loss, NIC queues            | Partly reducible through network design                 |

For ultra-low-latency communication between two nodes, the most productive question is therefore not simply whether TCP is expensive.

**It is which portion of end-to-end latency and CPU consumption comes from TCP's required semantics, and which comes from the Linux networking data path.**

**The central conclusion: TCP was designed to make communication correct and interoperable across unreliable, heterogeneous networks. Its costs are the consequences of those guarantees and of the general-purpose kernel implementation, not merely inefficiencies that can be tuned away.**
