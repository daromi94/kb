# Bandwidth and Throughput

Three metrics describe system performance. Using a water pipe analogy:

| Metric     | Definition                             | Unit            |
|------------|----------------------------------------|-----------------|
| Latency    | Time for one drop to traverse the pipe | Milliseconds    |
| Bandwidth  | Maximum capacity the pipe could hold   | Megabits/second |
| Throughput | Actual flow coming out right now       | Requests/second |

## The key distinction

**Bandwidth** is theoretical maximum capacity defined by hardware (1 Gbps
Ethernet, 54 Mbps WiFi).

**Throughput** is actual achieved rate, always less than or equal to bandwidth:

```
Throughput <= Bandwidth
```

You might have a 1000 Mbps connection (bandwidth) but only process 50 Mbps
(throughput) due to slow servers, packet loss, or inefficient code.

- Bandwidth says: "I *could* move 100 boxes per hour"
- Throughput says: "I *actually* moved 80 boxes this hour"

## Why software engineers focus on throughput

You rarely control the physical cables (bandwidth). You control the code that
determines how efficiently you use that capacity.

Inefficient code (locking, blocking, poor algorithms) produces low throughput
even with high bandwidth available.

## The fundamental tradeoff

Latency and throughput often trade against each other:

- **Improve throughput:** Batch requests together, maximizing resource
  utilization
- **Consequence:** Individual requests wait longer, increasing latency

The goal of latency engineering is achieving low latency without destroying
throughput.

## Related

- [Latency definition](latency-definition.md) - The stopwatch rule
- [Latency-throughput tradeoff](latency-throughput-tradeoff.md) - The pipelining
  tension
