# Byte Queue Limits

## 1. What is BQL?

**Byte Queue Limits (BQL)** is a Linux kernel mechanism that dynamically limits the amount of outstanding network transmission data queued at the network device driver level.

Its primary objective is to:

- Reduce excessive packet queueing latency.
- Prevent bufferbloat in network device transmit queues.
- Maintain high network throughput.
- Keep the network device busy without unnecessarily accumulating packets.
- Move excess queueing into higher-level queueing disciplines (qdiscs), where Linux has greater control over packet scheduling.

The fundamental principle is:

**Keep enough data queued to prevent device starvation, but no more than necessary.**

BQL is essentially a feedback-driven mechanism for controlling the amount of outstanding work submitted to a network device.

## 2. Understanding the Linux transmission path

Before understanding BQL, it is necessary to understand where packets accumulate when Linux transmits network traffic.

A simplified transmission path looks like this:

```text
+-----------------------------+
| Application                 |
+-----------------------------+
               |
               v
+-----------------------------+
| Socket                      |
| Send buffering              |
+-----------------------------+
               |
               v
+-----------------------------+
| TCP/IP networking           |
+-----------------------------+
               |
               v
+-----------------------------+
| Qdisc                       |
| Software packet queue       |
+-----------------------------+
               |
               v
+-----------------------------+
| Network driver              |
| TX descriptor ring          | <-- BQL operates here
+-----------------------------+
               |
               v
+-----------------------------+
| NIC                         |
| DMA and transmission        |
+-----------------------------+
               |
               v
            Network
```

There are multiple locations where data can accumulate.

However, two queues are particularly important:

| Queue          | Responsibility                                                               |
| -------------- | ---------------------------------------------------------------------------- |
| Qdisc          | Packet scheduling, prioritization, traffic shaping and congestion management |
| Driver TX ring | Holding descriptors for packets submitted to the network device              |

**Once packets have been handed to the driver and committed to transmission, the qdisc generally cannot reorder, prioritize or selectively drop them.**

This makes excessive queueing at the driver level particularly undesirable.

## 3. The problem: excessively large TX queues

A NIC operates asynchronously from the CPU.

The CPU prepares packets, creates TX descriptors, and notifies the NIC. The NIC fetches packet data through DMA and transmits it over the network.

```text
          CPU                              NIC
+---------------------+          +---------------------+
| Prepare packets     |          | Fetch packet data   |
| Create descriptors  |          | Transmit packets    |
+---------------------+          +---------------------+
           |                                ^
           v                                |
    +----+----+----+----+----+----+----+----+-----+
    | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | ... |
    +----+----+----+----+----+----+----+----+-----+
                  TX descriptor ring

       Producer                          Consumer
```

A large descriptor ring allows the CPU and NIC to operate independently for longer periods, reducing the risk of hardware starvation.

However, it also introduces the possibility of excessive buffering.

Consider a hypothetical TX ring containing 1,024 descriptors, each referencing a 1,500-byte packet:

```text
Descriptors:       1,024
Bytes per packet:  1,500
Outstanding data:  1,536,000 bytes
```

The approximate time required to drain this data is:

```text
T_drain = (Outstanding_bytes * 8) / Link_bitrate
```

| Link speed | Queue drain time |
| ---------- | ---------------- |
| 100 Mbps   | 122.88 ms        |
| 1 Gbps     | 12.29 ms         |
| 10 Gbps    | 1.23 ms          |
| 100 Gbps   | 122.88 us        |

These are simplified estimates that exclude protocol overhead and hardware-specific behavior.

At 1 Gbps, a newly submitted packet could experience approximately 12 milliseconds of additional latency just waiting for previously queued packets to be transmitted.

This is a form of **bufferbloat**.

### Head-of-line blocking

Consider a bulk file transfer competing with a latency-sensitive RPC.

```text
              Transmission direction
                       ---->

TX ring:

+-----+------+------+------+------+------+------+
| RPC | Bulk | Bulk | Bulk | Bulk | Bulk | Bulk | --> NIC
+-----+------+------+------+------+------+------+
   ^
   |
Latency-sensitive packet
```

Even if the RPC has higher priority, it generally cannot bypass packets already committed to the same hardware transmit queue.

The scheduling decision was made too early.

## 4. Why not simply make the TX ring smaller?

A small TX ring reduces queueing latency but increases the possibility of starvation.

Consider a NIC that consumes all its outstanding descriptors before the CPU can replenish them.

```text
Time --------------------------------------------->

NIC:  [Transmitting][ IDLE ][Transmitting][ IDLE ]
                        ^                     ^
                        |                     |
                 Waiting for CPU       Waiting for CPU
```

The NIC may become idle even though additional packets are waiting in the networking stack.

Replenishment can be delayed by:

- Interrupt moderation.
- TX completion batching.
- NAPI polling delays.
- CPU scheduling delays.
- CPU contention.
- Lock contention.
- Driver execution overhead.

A fixed queue capacity creates an undesirable trade-off.

| Small queue                   | Large queue                      |
| ----------------------------- | -------------------------------- |
| Low queueing latency          | High queueing latency            |
| Greater starvation risk       | Lower starvation risk            |
| Potential throughput loss     | Easier throughput saturation     |
| Less tolerance for CPU delays | Greater tolerance for CPU delays |

The optimal amount of outstanding data depends on runtime conditions.

This is the problem BQL solves.

## 5. Physical capacity vs. logical capacity

BQL does not dynamically resize the physical descriptor ring.

Instead, it introduces a **dynamic logical limit** on the amount of data outstanding.

```text
Physical TX ring capacity
+-------------------------------------------------+
|                                                 |
|   BQL permitted outstanding data                |
|   +--------------------+                        |
|   |                    |                        |
|   +--------------------+                        |
|                                                 |
+-------------------------------------------------+

    <---- BQL limit ----->
<--------------- Physical capacity --------------->
```

For example:

```text
Physical ring:      1,024 descriptors
Physical capacity:  Unchanged
Current BQL limit:  32 KB
Outstanding data:   24 KB
Available budget:   8 KB
```

The physical ring remains available to accommodate larger workloads when necessary, but BQL controls how much of it should be occupied under current conditions.

**The descriptor capacity and the byte limit are independent constraints.**

## 6. How BQL works internally

BQL is built on a generic Linux kernel mechanism called **Dynamic Queue Limits (DQL)**.

DQL maintains accounting for a producer-consumer queue.

The three fundamental quantities are:

| Quantity        | Meaning                                |
| --------------- | -------------------------------------- |
| `num_queued`    | Cumulative bytes submitted             |
| `num_completed` | Cumulative bytes reported as completed |
| `limit`         | Current outstanding byte budget        |

Outstanding data is calculated as:

```text
Outstanding = Queued - Completed
```

The remaining budget is:

```text
Available = Limit - Outstanding
```

For example:

```text
Total submitted:   100 KB
Total completed:   76 KB
Outstanding:       24 KB

BQL limit:         32 KB
Available budget:  8 KB
```

This accounting avoids having to walk the descriptor ring to determine the amount of outstanding work.

### Enqueue path

When the driver submits packet data to the NIC, it reports the corresponding byte count to BQL.

```text
       Qdisc
         |
         v
Driver TX function
         |
         +----> Submit TX descriptors
         |
         +----> Report bytes to BQL
                         |
                         v
                 Update accounting
                         |
                         v
                 Budget exceeded?
                         |
          +--------------+--------------+
          |                             |
         Yes                           No
          |                             |
          v                             v
     Stop queue                     Continue
```

If outstanding bytes exceed the current limit, BQL signals the networking stack to stop supplying additional packets to that transmit queue.

### Completion path

When the driver processes completed transmissions, it reports the completed byte count.

```text
NIC consumes descriptors
            |
            v
TX completion processing
            |
            +----> Reclaim descriptors
            |
            +----> Report completed bytes
                              |
                              v
                    Update BQL accounting
                              |
                              v
                    Adjust dynamic limit
                              |
                              v
                      Budget available?
                              |
               +--------------+--------------+
               |                             |
              Yes                           No
               |                             |
               v                             v
         Resume queue                 Remain stopped
```

The completion path both releases outstanding byte budget and provides feedback for adjusting the limit.

Importantly, completion is based on driver-reported TX completions, not TCP acknowledgments from the remote endpoint.

## 7. The adaptive algorithm

BQL continuously attempts to discover the smallest outstanding byte budget that avoids device starvation.

It reacts to two important conditions: **starvation** and **slack**.

### Condition A: starvation

Assume the BQL limit is too small.

```text
BQL limit = 16 KB

Outstanding bytes

16 KB |*****         *****
      |     *       *     *
      |      *     *       *
      |       *   *         *
 0 KB |        ***           ***
      +----------------------------> Time
                ^             ^
                |             |
           Starvation    Starvation
```

The NIC consumes the available work before completion processing allows the networking stack to submit additional data.

When DQL detects evidence that its limit caused or could have caused starvation, it increases the limit.

```text
Previous limit:  16 KB
New limit:       32 KB
```

The additional outstanding data gives the CPU more time to process completions and replenish the NIC.

### Condition B: excessive slack

Assume the BQL limit is larger than necessary.

```text
BQL limit = 128 KB

Outstanding bytes

128 KB |********************************
       |
       |       Excessive buffering
       |
       |--------------------------------
       |       Minimum useful data
       |
  0 KB +--------------------------------> Time
```

If the queue consistently contains more work than necessary to keep the consumer busy, DQL gradually reduces its limit.

```text
128 KB
   |
   v
 96 KB
   |
   v
 64 KB
   |
   v
 32 KB
```

DQL observes slack over multiple completion intervals before reducing the limit, rather than reacting aggressively to individual fluctuations.

The actual algorithm considers previous over-limit conditions, outstanding data across completion intervals, recently completed bytes, enqueue granularity, and minimum observed slack. **An empty queue alone is not sufficient evidence of starvation: there might simply be no traffic to send.**

### Simplified feedback loop

```text
          +--------------------+
          | Current BQL limit  | <-------------+
          +--------------------+               |
                     |                         |
                     v                         |
          +--------------------+               |
          | Observe queue      |               |
          | during completion  |               |
          +--------------------+               |
                     |                         |
     +---------------+---------------+         |
     |               |               |         |
     v               v               v         |
Starvation        Stable       Excess slack    |
     |               |               |         |
     v               v               v         |
 Increase        Maintain        Decrease      |
     |               |               |         |
     +---------------+---------------+         |
                     |                         |
                     v                         |
          +--------------------+               |
          | Updated BQL limit  |               |
          +--------------------+               |
                     |                         |
                     +-------------------------+
```

BQL is an adaptive queue-depth controller, not a fixed queue configuration.

## 8. The mathematical intuition

The minimum useful amount of outstanding data depends on two fundamental quantities:

- The rate at which the device consumes data.
- The time required for the producer to replenish it.

A simplified performance model is:

```text
B_min ~= R * T_refill
```

Where:

- **`B_min`:** minimum useful outstanding bytes.
- **`R`:** device consumption rate in bytes per second.
- **`T_refill`:** effective replenishment delay.

For a 10 Gbps NIC:

```text
R = 1.25 * 10^9 bytes/s
```

Assuming a replenishment delay of 20 microseconds:

```text
B_min ~= 1.25 * 10^9 * 0.000020
```

```text
B_min ~= 25,000 bytes
```

| Replenishment delay | Approximate useful buffering at 10 Gbps |
| ------------------- | --------------------------------------- |
| 5 us                | 6.25 KB                                 |
| 10 us               | 12.5 KB                                 |
| 20 us               | 25 KB                                   |
| 50 us               | 62.5 KB                                 |
| 100 us              | 125 KB                                  |

This is an analytical model, not the literal BQL algorithm.

It illustrates an important systems engineering relationship:

**The slower the producer responds to consumer progress, the more outstanding work is required to maintain consumer utilization.**

This is closely related to Little's Law:

```text
L = lambda * W
```

Maintaining high throughput while reducing replenishment delay makes it possible to operate with less outstanding work.

## 9. Why limit bytes instead of packets?

Packets have different sizes.

Consider a packet-based queue limit of 100 packets.

```text
Workload A:

100 packets * 64 bytes = 6,400 bytes

Workload B:

100 packets * 1,500 bytes = 150,000 bytes
```

At 1 Gbps:

| Workload | Outstanding bytes | Idealized drain time |
| -------- | ----------------- | -------------------- |
| A        | 6,400             | 51.2 us              |
| B        | 150,000           | 1,200 us             |

The number of packets is identical, but the transmission work differs substantially.

The problem becomes even more significant with:

- Generic Segmentation Offload (GSO).
- TCP Segmentation Offload (TSO).
- Jumbo frames.
- Scatter-gather DMA.

A single `sk_buff` may represent tens of kilobytes of data that will eventually become multiple network packets.

Likewise, a single packet may require multiple descriptors.

```text
                    One skb
   +---------------------------------------+
   | 64 KB of TCP data                     |
   +---------------------------------------+
                       |
                       v
               NIC segmentation
                       |
                       v
+-------+-------+-------+-------+-----+-------+
| Frame | Frame | Frame | Frame | ... | Frame |
+-------+-------+-------+-------+-----+-------+
```

Packet counts and descriptor counts are therefore imperfect representations of transmission work.

Byte-based accounting correlates more closely with the amount of time needed to transmit outstanding data, although it is not an exact measure of wire occupancy.

## 10. BQL moves queueing to the right layer

Perhaps the most important architectural benefit of BQL is not simply reducing queue depth. It is controlling **where queueing occurs**.

### Without BQL

```text
Qdisc                          Driver TX queue

+---+---+                      +---+---+---+---+---+-----+
| A | B | -------------------> | C | D | E | F | G | ... | --> NIC
+---+---+                      +---+---+---+---+---+-----+

Little software queueing       Excessive driver queueing
```

Most outstanding packets are beyond the control of the software scheduler.

### With BQL

```text
Qdisc                          Driver TX queue

+---+---+---+---+---+---+      +---+---+
| A | B | C | D | E | F | ---> | G | H | --> NIC
+---+---+---+---+---+---+      +---+---+

Software-controlled queue      Small hardware backlog
```

Packets remain in a layer that can implement sophisticated scheduling policies.

For example, with FQ-CoDel:

```text
              Qdisc
+-------------------------------+
| Flow A: [Bulk][Bulk][Bulk]    |
| Flow B: [RPC]                 |
| Flow C: [ACK][ACK]            |
+-------------------------------+
                |
         Flow scheduler
                |
                v
         +-------------+
         | Small TX    |
         | backlog     |
         +-------------+
                |
                v
               NIC
```

FQ-CoDel can isolate competing flows and manage persistent queueing delay while BQL limits the amount of work already committed to the driver.

The mechanisms are complementary:

| Mechanism              | Responsibility                                       |
| ---------------------- | ---------------------------------------------------- |
| BQL                    | Control driver-level outstanding bytes               |
| FQ-CoDel               | Flow isolation and active queue management           |
| FQ                     | Flow scheduling and pacing                           |
| TCP congestion control | Control sending behavior based on network conditions |

BQL does not eliminate queueing. It makes queueing more manageable.

## 11. BQL in multiqueue NICs

Modern NICs typically expose multiple TX queues.

**BQL operates independently for each supported network device transmit queue.**

```text
                 Networking stack
                         |
                TX queue selection
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
+-------------+   +-------------+   +-------------+
| TX Queue 0  |   | TX Queue 1  |   | TX Queue 2  |
| BQL: 32 KB  |   | BQL: 64 KB  |   | BQL: 16 KB  |
+-------------+   +-------------+   +-------------+
       |                 |                 |
       v                 v                 v
+-------------+   +-------------+   +-------------+
| TX Ring 0   |   | TX Ring 1   |   | TX Ring 2   |
+-------------+   +-------------+   +-------------+
       |                 |                 |
       +-----------------+-----------------+
                         |
                         v
                        NIC
```

Different queues can converge toward different limits because they experience different traffic patterns, CPU contention, completion behavior, and scheduling delays.

This also means that a per-queue BQL limit is not a global bound on all outstanding data inside the NIC.

## 12. What BQL does not do

Several distinctions are important.

| Mechanism                                       | BQL? |
| ----------------------------------------------- | ---- |
| Dynamically control outstanding TX bytes        | Yes  |
| Resize the physical descriptor ring             | No   |
| Directly limit application sending rate         | No   |
| Drop packets as a congestion policy             | No   |
| Provide per-flow fairness                       | No   |
| Perform TCP congestion control                  | No   |
| Control RX queue depth                          | No   |
| Directly target a specific latency percentile   | No   |
| Eliminate buffering inside switches and routers | No   |

BQL is also not a strict byte ceiling. Since accounting occurs at submission time, individual packets or batches can cause outstanding bytes to exceed the limit before subsequent submissions are stopped.

## 13. Engineering lessons

### Bound outstanding work instead of maximizing queue capacity

A large physical capacity can be useful, but continuously filling that capacity is rarely necessary.

```text
     Too little work       Optimal region     Too much work
    Device starvation     Full utilization   Excess latency

Throughput
^
|                    ____/-----------------------------------
|               ____/
|          ____/
|     ____/
|____/
+------------------------+-----------------+-----------------> Queue depth

Queueing latency
^
|                                                        ___/
|                                                   ____/
|                                           _______/
|                         _________________/
|________________________/
+------------------------+-----------------+-----------------> Queue depth
```

Once the consumer is saturated, additional outstanding work primarily increases waiting time rather than throughput.

### Keep queues where scheduling decisions remain possible

Work committed to a low-level execution mechanism becomes harder to reorder, cancel, prioritize, or shed.

This principle applies beyond networking:

| System                   | Scheduling layer     | Lower-level execution queue |
| ------------------------ | -------------------- | --------------------------- |
| Linux networking         | Qdisc                | NIC TX ring                 |
| Distributed query engine | Task scheduler       | Worker execution queue      |
| Storage engine           | I/O scheduler        | Device submission queue     |
| Inference engine         | Request scheduler    | GPU execution pipeline      |
| RPC service              | Admission controller | Thread pool queue           |

**Keeping lower-level queues small preserves scheduling flexibility.**

### Improve feedback latency to reduce buffering requirements

A faster producer-consumer feedback loop reduces the amount of outstanding work needed to maintain utilization.

```text
     Slow completion feedback
                 |
                 v
  Larger outstanding work budget
                 |
                 v
Greater potential queueing latency

     Fast completion feedback
                 |
                 v
  Smaller outstanding work budget
                 |
                 v
 Lower potential queueing latency
```

This explains why interrupt moderation, completion batching, CPU scheduling, and queue-depth control are interconnected performance concerns.

## 14. Mental model

BQL is best understood as the combination of four engineering patterns:

- Adaptive queue-depth control.
- Credit-based flow control.
- Completion-driven backpressure.
- Starvation avoidance.

```text
                      BQL
               +---------------+
               | Dynamic byte  |
               | budget        |
               +---------------+
                       |
                       v
Producer ----------> Queue ----------> Consumer
    ^                                      |
    |                                      |
    +-------- Completion feedback ---------+
```

**The goal is not to keep the queue full. The goal is to keep the consumer busy with the smallest necessary amount of outstanding work.**
