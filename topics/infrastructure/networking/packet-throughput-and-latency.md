# How should a network transport maximize packet throughput while minimizing per-packet latency?

Consider two nodes communicating over a network link. Every packet fits within a single MTU, so IP fragmentation is unnecessary.

The objective is to transmit as many packets per second as possible while keeping the one-way delivery latency of each packet as low and predictable as possible.

This raises three questions:

1. Is this fundamentally a throughput optimization problem, a latency optimization problem, or both?
2. Does maximizing throughput necessarily increase latency?
3. How should a transport system balance packet-processing efficiency, link utilization, queueing, and latency?

## 1. Throughput and latency are different properties

Consider a simplified communication path:

```text
   Node A                          Node B

 Application                     Application
      |                               ^
      v                               |
Network stack                   Network stack
      |                               ^
      v                               |
  TX Queue                        RX Queue
      |                               ^
      v                               |
     NIC -------- Network ---------> NIC
```

Two important performance properties describe this system.

Throughput measures how much work the system completes per unit of time.

Since the objective involves transmitting individual packets, packets per second (PPS) is particularly relevant.

```text
Packet throughput = packets successfully delivered / second
```

Bandwidth utilization, typically expressed in Gbps, is another relevant metric, but high bandwidth throughput does not necessarily imply high packet throughput.

Latency measures how long an individual packet takes to travel from one point to another.

```text
L = t_arrival - t_departure
```

The measurement boundaries matter. NIC-to-NIC latency excludes application and kernel processing, while application-to-application latency includes them.

For an application-level transport, a useful decomposition is:

```text
L_total = L_sender + L_network + L_receiver
```

Each component may include processing and queueing delays.

### A crucial distinction: capacity versus achieved throughput

A transport system has some maximum sustainable processing capacity, `mu`, measured in packets per second.

Applications offer traffic at a rate `lambda`.

These values are different:

- `mu`: How many packets the system could process per second.
- `lambda`: How many packets arrive per second.
- `X`: How many packets are successfully delivered per second.

For a stable, lossless system under sustained traffic:

```text
X = lambda, when lambda < mu
```

Maximizing processing capacity is generally beneficial because it allows more traffic to be handled without congestion.

Maximizing offered traffic until the system saturates, however, is not necessarily beneficial.

The objective should be to increase system capacity without creating excessive queueing delay.

## 2. The throughput-latency relationship

Throughput and latency are not inherently opposed.

At low utilization, a system can increase throughput without significantly increasing latency.

The problem begins when the offered load approaches the system's processing capacity.

Consider a receiver capable of processing one million packets per second.

```text
Packet arrivals
     |
     v
Receive queue
     |
     v
Packet processor
     |
     v
Application

Processing capacity: 1,000,000 PPS
```

As arrivals approach this capacity, packets become increasingly likely to wait in a queue.

Under a simplified M/M/1 queueing model, average response time is:

```text
W = 1 / (mu - lambda)
```

This assumes a single server, independent exponentially distributed service times, Poisson arrivals, and a stable queue.

```text
Illustrative M/M/1 queue, capacity 1,000,000 PPS (mean time in system)

Utilization  (each # = 2.4 us)
10% | #                                                     1.1 us
30% | #                                                     1.4 us
50% | #                                                     2.0 us
70% | #                                                     3.3 us
80% | ##                                                    5.0 us
90% | ####                                                 10.0 us
95% | ########                                             20.0 us
99% | ##########################################          100.0 us
      +---------+---------+---------+---------+---------+
      0        24        48        72        96        120 us

M/M/1 example, not measured network latency.
```

Notice what happens:

| Utilization | Delivered packets/sec | Mean time in modeled system |
| ----------- | --------------------- | --------------------------- |
| 50%         | 500,000               | 2 µs                        |
| 80%         | 800,000               | 5 µs                        |
| 90%         | 900,000               | 10 µs                       |
| 99%         | 990,000               | 100 µs                      |

Increasing throughput from 900,000 to 990,000 PPS improves throughput by just 10%, but increases mean latency tenfold.

Actual network behavior depends on burstiness, packet sizes, number of processing stages, scheduling, and buffering. The M/M/1 example demonstrates why high utilization can be dangerous; it is not a universal latency prediction.

### The knee of the curve

In networking, an important concept is the knee of the throughput-delay curve.

Below this point, additional traffic produces useful throughput without excessive queueing.

Beyond this point, delays rise disproportionately while delivered throughput approaches its maximum.

The correct operating point is therefore not necessarily 100% utilization. It depends on the workload, burstiness, and acceptable latency.

## 3. Packet throughput is not the same as bandwidth throughput

For packets smaller than one MTU, an important limitation is often packet-processing capacity rather than raw link bandwidth.

Consider a 10 Gbps Ethernet link.

| Ethernet frame size | Theoretical maximum packet rate |
| ------------------- | ------------------------------- |
| 64 bytes            | 14.88 million PPS               |
| 128 bytes           | 8.45 million PPS                |
| 512 bytes           | 2.35 million PPS                |
| 1518 bytes          | 812,744 PPS                     |

These calculations include Ethernet preamble and interframe gap overhead, and assume a continuously transmitting link without additional encapsulation.

The smaller the packets, the more packets the system must process to utilize the same link bandwidth.

This matters because the kernel and NIC perform work per packet, including:

- Descriptor management and DMA operations.
- Packet metadata processing.
- Protocol processing.
- Queue management.
- Interrupt or polling operations.

For small packets, per-packet overhead can become the bottleneck before the physical link reaches capacity.

Therefore, optimizing packet throughput often means reducing CPU cycles and fixed overhead per packet, rather than increasing link bandwidth.

## 4. When do throughput and latency conflict?

There are two fundamentally different ways to increase throughput.

### Approach A: Make packet processing faster

Suppose a processing stage takes 2 microseconds per packet.

Its maximum processing rate, assuming one serial worker, is:

```text
mu = 1 / (2 us) = 500,000 PPS
```

Now suppose an optimization reduces processing time to 1 microsecond.

The processing rate becomes:

```text
mu = 1,000,000 PPS
```

Both properties improve:

- Maximum throughput doubles.
- Processing latency is halved.
- Queueing pressure decreases for the same offered load.

This is a genuine improvement in system efficiency.

Techniques such as avoiding unnecessary copies, improving cache locality, reducing synchronization, and eliminating redundant processing can improve both throughput and latency.

### Approach B: Accumulate more work

Another approach is to collect packets into batches before processing them.

```text
Without intentional batching:

Packet A --------> Process immediately
Packet B --------> Process immediately
Packet C --------> Process immediately

With intentional batching:

Packet A ---\
Packet B ----+----> Process batch [ A, B, C ]
Packet C ---/
```

Batching can amortize fixed costs and improve packet throughput.

However, if a packet must wait for other packets to arrive before the batch can be processed, that waiting increases latency.

This introduces a trade-off:

| Strategy                                              | Throughput                    | Per-packet latency         |
| ----------------------------------------------------- | ----------------------------- | -------------------------- |
| Process immediately                                   | Potentially higher overhead   | Usually lower waiting time |
| Wait to form large batches                            | Potentially higher efficiency | Higher waiting time        |
| Process currently available packets in bounded bursts | Good efficiency               | Often a useful compromise  |

An important subtlety: batch processing does not necessarily introduce latency. Processing packets that have already arrived in a batch is different from intentionally delaying packets to accumulate a batch.

DPDK explicitly supports different processing strategies, from individual packet processing to burst-oriented execution, because there is no universally optimal strategy.

## 5. Queueing is the most important source of the trade-off

Consider two packets arriving at a transmit queue.

```text
        Node A

 Packet A    Packet B
     |           |
     v           v
+---------------------+
|      TX Queue       |
+---------------------+
           |
           v
          NIC
           |
           v
     Network link
```

A physical link cannot serialize two Ethernet frames simultaneously on the same transmission channel.

If Packet A is being transmitted, Packet B must wait.

For example, transmitting a 1,000-byte Ethernet frame on a 10 Gbps link takes approximately:

```text
T_serialization = (1000 * 8) / 10^10 = 0.8 us
```

This excludes preamble and interframe gap overhead, which increase the occupied wire time to approximately 0.816 microseconds per frame.

If 50 such frames are queued ahead of a packet, they alone can add approximately 40.8 microseconds of waiting.

The important observation is:

Queueing latency depends on the amount of work ahead of a packet, not just how fast the packet itself can be transmitted.

Queues are necessary to accommodate bursts, but continuously occupied queues introduce avoidable latency.

This is the problem addressed by queue management mechanisms such as AQM. Keeping queues normally short can improve both latency and throughput.

## 6. What should be optimized in a Linux transport?

There are several approaches, each targeting a different source of overhead.

| Optimization               | Potential throughput benefit       | Potential latency benefit                    |
| -------------------------- | ---------------------------------- | -------------------------------------------- |
| Reduce per-packet CPU work | Higher PPS capacity                | Lower processing latency                     |
| Reduce unnecessary copies  | Less memory/CPU overhead           | Shorter critical path                        |
| NIC interrupt coalescing   | Fewer interrupts per packet        | May worsen latency through intentional delay |
| Busy polling               | Avoids interrupt/wakeup overhead   | Can reduce wakeup latency                    |
| Bounded batching           | Amortizes fixed costs              | Depends on whether packets are held          |
| Multiple NIC RX/TX queues  | Distributes processing across CPUs | Reduces bottleneck queueing                  |
| Packet pacing              | Smoother traffic                   | Reduces burst-induced queueing               |
| Control queue depth        | May reduce waste and congestion    | Reduces queueing latency                     |

Busy polling trades CPU cycles for lower latency. Deferred interrupts can improve batching at the cost of latency under light load.

Receive queues should be configured based on CPU capacity and queueing behavior rather than simply maximizing queue count.

## 7. How should the optimization objective be formulated?

Rather than maximizing throughput without constraints, the problem can be formulated as:

Maximize the sustainable packet delivery rate subject to a latency and reliability requirement.

Mathematically:

```text
maximize   X_delivered

subject to L_p99.9   <= L_target
           P_loss    <= epsilon
           CPU usage <= CPU budget
```

Where:

- `X_delivered` is the actual packet delivery rate.
- `L_p99.9` is the 99.9th-percentile one-way latency.
- `L_target` is the allowed latency.
- `epsilon` is the acceptable packet-loss probability.

The latency target should be measured for a precisely defined path, such as application-to-application or NIC-to-NIC.

For meaningful one-way latency measurements across machines, clocks need adequate synchronization. Linux supports hardware packet timestamping where the NIC and driver provide it.

### An example optimization experiment

Suppose three transport configurations produce these hypothetical results:

| Configuration           | Delivered PPS | p99.9 latency | Loss |
| ----------------------- | ------------- | ------------- | ---- |
| A: Aggressive batching  | 2.0 million   | 200 µs        | 0%   |
| B: Bounded batching     | 1.7 million   | 30 µs         | 0%   |
| C: Immediate processing | 1.2 million   | 15 µs         | 0%   |

If the latency requirement is 50 microseconds, configuration B provides the highest throughput while meeting the requirement.

If the requirement is 20 microseconds, configuration C becomes preferable.

This is a constrained optimization problem, rather than simply a throughput benchmark.

A useful benchmarking strategy is to increase offered load gradually, measuring delivered PPS, latency distributions, and loss at each step. The resulting measurements reveal the practical throughput-latency operating frontier.

## 8. Can maximum throughput and minimum latency coexist?

Yes, under certain conditions.

Imagine a perfectly paced stream of packets whose arrival rate matches the service capacity of a link.

```text
Time ---------------------------------------------->

Packets arriving:
  A    B    C    D    E    F
  |    |    |    |    |    |
  v    v    v    v    v    v

Link transmission:
[ A ][ B ][ C ][ D ][ E ][ F ]

Queue waiting:
  0    0    0    0    0    0
```

In this idealized deterministic system:

- The link can remain fully utilized.
- Each packet begins transmission immediately.
- No queue needs to accumulate.
- Per-packet latency remains close to its minimum.

This demonstrates that maximum throughput and minimum latency are not fundamentally mutually exclusive.

The difficulty in real systems is variability.

Packets may arrive in bursts. Processing times fluctuate. NIC queues can temporarily fill. The scheduler can delay an execution context. Other traffic may compete for resources.

These sources of variability create queueing even when average traffic remains below maximum capacity.

Consequently, real systems generally need some headroom to maintain predictable latency.

## 9. The fundamental conclusion

There are two very different optimization strategies:

- **Increasing capacity:** Reduce the amount of time and resources required to process each packet. This can improve both throughput and latency.
- **Increasing utilization:** Push more packets through the existing system. This improves achieved throughput up to capacity, but can dramatically increase queueing latency near saturation.

The strongest design objective for a low-latency, high-throughput transport is therefore:

> Maximize sustainable packets per second while minimizing the processing and queueing latency experienced by each packet, particularly at high-percentile latency targets.

It is not about keeping the CPU or NIC as busy as possible. It is about making each packet inexpensive to process, avoiding unnecessary waiting, and operating within the capacity of the slowest stage.
