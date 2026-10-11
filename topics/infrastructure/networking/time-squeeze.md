# Time squeeze

In Linux networking, time squeeze is a per-CPU counter that records occasions when the network receive-processing softirq exhausts its processing budget or time allowance.

It is associated with `NET_RX_SOFTIRQ`, which processes incoming network traffic through NAPI.

The basic idea:

> Linux deliberately limits how much network-processing work can be performed in one softirq cycle, preventing network traffic from monopolizing CPU execution.

When that limit is reached, Linux stops the current receive-processing cycle and schedules further processing if work remains.

### A simplified example

Imagine a CPU receives 1,000 packets, but the networking subsystem is configured to process at most 300 packets per polling cycle.

```text
                  NIC receives
                  1000 packets
                       |
                       v
                +-------------+
                | NAPI Poll   |
                |             |
                | Budget: 300 |
                +------+------+
                       |
                       v
                Process packets
                   1 ... 300
                       |
                       v
                Budget exhausted
                       |
                       v
                 TIME SQUEEZE
                       |
                       v
               End current cycle
                       |
                       v
                Remaining work
                processed later
```

The packets are not necessarily dropped. Processing is deferred to another opportunity.

The name is slightly misleading: the counter can increase because either the packet budget or the time limit was exhausted.

## 2. Why does Linux impose these limits?

Consider a machine running two kinds of work:

- A network-heavy application receiving millions of packets.
- Other threads that also need CPU time.

Without limits, network receive processing could potentially occupy the CPU for excessively long periods.

```text
             CPU EXECUTION

Without a processing limit:

+---------------------------------------------+
| NETWORK NETWORK NETWORK NETWORK NETWORK ... |
+---------------------------------------------+

Other runnable work experiences delays.
```

With a bounded receive-processing cycle:

```text
             CPU EXECUTION

+------------+-----------+------------+------------+
| Network RX | Other work| Network RX | Other work |
+------------+-----------+------------+------------+
```

This is a conceptual illustration; the real scheduler does not alternate work in such fixed intervals.

The objective is to prevent networking softirq execution from causing excessive delays to other system activity.

Linux therefore places bounds on how much work the `NET_RX_SOFTIRQ` handler performs before yielding its current processing opportunity.

This is a general operating-system design principle: high-throughput background work must be balanced against scheduling fairness and latency.

## 3. Two limits control time squeeze

Linux exposes two important settings:

```bash
sysctl net.core.netdev_budget
sysctl net.core.netdev_budget_usecs
```

Common example values are:

```text
net.core.netdev_budget       = 300
net.core.netdev_budget_usecs = 2000
```

These settings apply to a CPU's NAPI receive-processing cycle, across the NAPI instances serviced by that cycle—not separately to every socket or NIC.

| Parameter             | Meaning                                     |
| --------------------- | ------------------------------------------- |
| `netdev_budget`       | Maximum RX packet-processing work budget    |
| `netdev_budget_usecs` | Approximate time allowance, in microseconds |

The processing loop stops when either limit is reached.

### Example A: Packet budget exhausted

Suppose processing 300 packets takes only 800 microseconds.

```text
Configured limits:
  Packets: 300
  Time:    2000 us

Time elapsed
0       500      800              2000 us
|--------|--------|-------------------|
                  ^
                  |
          300 packets processed

Result:
  Packet budget exhausted
  Time allowance not exhausted
  Time squeeze increments
```

### Example B: Time allowance exhausted

Suppose packet processing is expensive, and after approximately 2,000 microseconds only 180 packets have been processed.

```text
Configured limits:
  Packets: 300
  Time:    2000 us

Time elapsed
0             1000              2000 us
|---------------|-------------------|
                                    ^
                                    |
                           180 packets processed

Result:
  Time allowance exhausted
  Packet budget not exhausted
  Time squeeze increments
```

The counter cannot distinguish these two situations. Despite its name, `time_squeeze` measures either kind of budget exhaustion.

## 4. How time squeeze works internally

The relevant function is `net_rx_action()` in `net/core/dev.c`.

A simplified version of its logic:

```c
budget = netdev_budget;
deadline = now + netdev_budget_usecs;

while (napi_work_available()) {
    work = napi_poll(next_napi(), budget);
    budget -= work;

    if (budget <= 0 || deadline_reached()) {
        softnet_data->time_squeeze++;
        break;
    }
}

if (work_remains())
    schedule_net_rx_softirq();
```

This is illustrative pseudocode; actual timing checks and NAPI scheduling are more complex.

The important detail is what happens after the limit is reached.

```text
                NET_RX_SOFTIRQ
                      |
                      v
                 net_rx_action()
                      |
                      v
                 NAPI poll()
                      |
                      v
                Process packets
                      |
                      v
               Budget exhausted?
                    /     \
                  No       Yes
                   |        |
                   v        v
                Continue  time_squeeze++
                            |
                            v
                      Defer remaining
                          work
                            |
                            v
                      NET_RX_SOFTIRQ
                      runs again later
```

Under prolonged softirq pressure, deferred processing may run through the per-CPU `ksoftirqd/N` kernel thread. Linux also supports threaded NAPI configurations.

This is not equivalent to discarding packets. It means the current processing opportunity ended before all eligible work was completed.

## 5. Relationship between time squeeze and packet drops

Time squeeze and packet drops are related, but they are not equivalent.

Consider:

```text
                   NIC RX Ring
                +---------------+
                | Incoming data |
                +-------+-------+
                        |
                        v
                  NAPI processing
                        |
                  Budget exhausted
                        |
                        v
                   Time squeeze
                        |
                        v
                  Work deferred
                        |
                        v
                NIC continues receiving
                        |
                        v
                Can buffers keep up?
                    /       \
                  Yes        No
                   |          |
                   v          v
                No drops   RX ring or
                           other buffers
                           may overflow
                                |
                                v
                           Packet drops
```

Time squeeze is a signal that receive processing is reaching its configured execution limits, not proof that packets are being dropped.

Under persistent heavy traffic, repeated deferral can increase the backlog. If available buffering becomes exhausted, packet drops can follow.

It can also contribute to increased network-processing latency even without packet loss.

## 6. How to inspect time squeeze in Linux

The relevant kernel interface is:

```bash
cat /proc/net/softnet_stat
```

Each line represents one online CPU, and the counters are hexadecimal.

The first three columns are particularly useful:

| Column | Meaning                      |
| ------ | ---------------------------- |
| 1      | Processed packets/work count |
| 2      | Software networking drops    |
| 3      | Time squeeze events          |

### Example

```text
CPU    Processed     Dropped     Time squeeze
0      12900000      0           0
1      15300000      0           4521
2      11800000      0           0
3      10400000      0           0
```

This is illustrative data converted to decimal.

CPU 1 stands out: its networking processing repeatedly exhausted the budget or time limit.

Also check:

```bash
# Network receive softirq execution counts
grep NET_RX /proc/softirqs

# Per-CPU software interrupt utilization
mpstat -P ALL 1

# NIC/driver counters
ethtool -S eth0
```

## 7. Why time squeeze may increase on only one CPU

A particularly interesting situation is that most cores appear idle, but one CPU experiences substantial time squeeze.

```text
               NIC with RSS

                   NIC
                    |
             +------+------+
             |      |      |
             v      v      v
           RX 0   RX 1   RX 2
             |      |      |
             v      v      v
           CPU 0  CPU 1  CPU 2

           10%    100%    15%
                  ^^^^
               Bottleneck
```

This can happen when incoming traffic is unevenly distributed across RX queues.

Possible explanations include:

- One or a small number of high-volume flows concentrated on a single RX queue.
- Uneven RSS distribution.
- Poor IRQ affinity.
- Excessive per-packet processing cost.
- Competition with other CPU-intensive workloads.

Increasing the global processing budget may reduce the counter but leave the underlying imbalance unresolved.

## 8. Should the networking budget be increased?

Possibly, but not automatically.

For example, to experiment with larger limits:

```bash
sudo sysctl -w net.core.netdev_budget=600
sudo sysctl -w net.core.netdev_budget_usecs=4000
```

These changes are runtime changes and normally do not persist after reboot.

However, there is a tradeoff.

| Smaller budget                             | Larger budget                                  |
| ------------------------------------------ | ---------------------------------------------- |
| Shorter receive-processing cycles          | More work per cycle                            |
| More frequent opportunities for other work | Potentially fewer deferrals                    |
| May increase receive backlog               | May reduce receive backlog                     |
| May limit throughput under heavy traffic   | Can increase scheduling latency for other work |

Increasing a budget does not add CPU capacity. It permits network receive processing to use more of an execution opportunity before yielding.

For a latency-sensitive application, that may even be counterproductive.

A sound troubleshooting sequence is to observe the rate of time squeeze events, verify whether packet drops or tail latency are actually increasing, inspect CPU and RX-queue distribution, then adjust budgets only if the measurements support it.

## 9. Time squeeze versus other Linux networking counters

| Metric                    | What it indicates                                                 |
| ------------------------- | ----------------------------------------------------------------- |
| Time squeeze              | Receive-processing cycle exhausted its work/time allowance        |
| Softnet drops             | Packets dropped in software receive processing                    |
| NIC RX drops              | Hardware/driver receive failures or discards                      |
| TCP receive-queue drops   | Data could not be admitted to TCP receive state in relevant paths |
| UDP receive-buffer errors | UDP datagram could not be queued due to receive buffering         |

The counters describe different layers of the packet path. They should not be treated as interchangeable.

## 10. The underlying systems principle

Time squeeze illustrates an important operating-systems concept: bounded work per scheduling opportunity.

Linux cannot simply give networking unlimited CPU execution whenever traffic arrives. It must coordinate packet processing with the rest of the machine.

```text
       Network traffic arrives
                   |
                   v
          Work needs CPU time
                   |
                   v
          Process bounded batch
                   |
                   v
         More work remaining?
              /         \
            No           Yes
             |            |
             v            v
          Finish       Defer work
                          |
                          v
                 Other work may run
                          |
                          v
                    Resume later
```

This is closely related to mechanisms used in distributed systems, including cooperative scheduling, bounded processing batches, execution quanta, and admission control.

The essential distinction: time squeeze measures the exhaustion of a processing opportunity, not the exhaustion of the network or a socket buffer.
