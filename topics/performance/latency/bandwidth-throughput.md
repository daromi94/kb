# Bandwidth and throughput

Three metrics describe system performance. Using a water pipe analogy:

| Metric     | Definition                             | Unit            |
|------------|----------------------------------------|-----------------|
| Latency    | Time for one drop to traverse the pipe | Milliseconds    |
| Bandwidth  | Maximum capacity the pipe could hold   | Megabits/second |
| Throughput | Actual flow coming out right now       | Requests/second |

## The key distinction

Throughput is always at most equal to bandwidth. A 1000 Mbps connection
might only deliver 50 Mbps due to slow servers, packet loss, or
inefficient code.

- Bandwidth: "I *could* move 100 boxes per hour"
- Throughput: "I *actually* moved 80 boxes this hour"

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
- [Latency-throughput tradeoff](latency-throughput-tradeoff.md) - Pipelining tension

---

Return to [Latency](_index.md)
