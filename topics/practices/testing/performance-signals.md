# Performance signals

A useful performance test reports four numbers: throughput, latency,
error rate, and resource saturation. Together they answer whether the
workload met its targets and, if not, where the system bent under the
load.

## The four signals

**Throughput.** How much work the system completes per unit time —
usually requests per second. The headline measure of capacity.

**Latency.** How long each unit of work takes. Always reported as a
distribution, never a single number.

**Error rate.** The fraction of requests that failed or timed out.
Throughput must be counted in *successful* requests per second — a
service returning fast 500s looks busy, but the work never landed.

**Resource saturation.** How much headroom each component has left:
CPU, memory, disk and network I/O, connection pools, thread counts.
Saturation explains *why* throughput plateaus or latency climbs,
which the headline numbers alone cannot tell you.

## Throughput and latency move together

The fundamental tension in any system under load is between throughput
and latency. As load increases, latency stays roughly flat up to a
point, then rises sharply once a bottleneck is hit. Locating that
knee is often the whole point of the test, because the throughput
just below it is the safe operating ceiling.

## Related

- [Latency percentiles](latency-percentiles.md) - Why averages hide tail pain
- [Saturation curve](saturation-curve.md) - The full shape of the bend
- [Performance testing](performance-testing.md) - The choices around the measurement

---

Return to [Testing](_index.md)
