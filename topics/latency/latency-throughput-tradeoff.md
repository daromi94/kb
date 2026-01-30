# Latency-Throughput Tradeoff

Latency and throughput represent fundamentally different optimization targets
that often conflict.

**Key asymmetry:**

- Bandwidth is fixable: buy more cables or network cards
- Latency is stuck: you cannot buy faster light

## The laundry analogy

Consider a washer (30 min) and dryer (60 min) processing multiple loads.

### Serial approach (latency-optimized)

Process one load completely before starting the next:

```
Load A: Wash (30m) → Dry (60m) = 90 minutes total
```

**Result:** Individual load completes in 90 minutes, but throughput is only 0.67
loads/hour.

### Pipelined approach (throughput-optimized)

Create a 60-minute "heartbeat" synchronized to the slowest stage (dryer):

```
Time 0:00  - Load A enters dryer, Load B enters washer
Time 0:30  - Load B finishes washing, WAITS for dryer
Time 1:00  - Load A exits, Load B enters dryer
Time 2:00  - Load B exits
```

**Load B's journey:**

- Washing: 30 minutes
- Waiting for dryer: 30 minutes (the penalty)
- Drying: 60 minutes
- **Total: 120 minutes**

**Result:** Individual load takes 120 minutes (worse latency), but throughput
improves to 1 load/hour (dryer never idles).

## The hidden waiting room

In pipelined systems, fast stages are held back by slow stages. The washer
finishes in 30 minutes but must wait 30 minutes for the dryer, adding idle time
to each item's latency.

This explains why high-throughput systems (Kafka, batch processors) feel "slow"
to individual users - they use queues and buffers to keep resources fully
utilized.

## The choice

| Optimization target | Strategy                   | Consequence             |
|---------------------|----------------------------|-------------------------|
| Low latency         | No queuing, idle resources | Inefficient utilization |
| High throughput     | Pipelining, batching       | Items wait in queues    |

- **Low latency:** The single user is happy, but machines sit idle
- **High throughput:** Machines are always busy, but users wait in line

## Related

- [Dennard scaling](dennard-scaling.md) - Why parallelism became necessary
- [Bandwidth and throughput](bandwidth-throughput.md) - Distinguishing the
  metrics
