# Saturation curve

A system under rising load passes through four phases. Each one ends
when a shared resource hits its limit, and the next reveals how the
system handles that contention. The whole point of a load test is to
walk this curve before production does.

## The four phases

**Linear scalability.** Throughput grows in lockstep with concurrency.
Latency stays low and flat. Resources are abundant and queues are
empty.

**The knee.** A shared resource — CPU threads, memory bandwidth, a
database connection pool — approaches its limit. Throughput stops
growing in proportion to offered load and queues begin to form. The
slope of the throughput curve bends.

**Saturation.** The system reaches its maximum capacity. Throughput
plateaus. New requests wait in queues rather than running, so latency
climbs steeply — exponentially as utilization approaches 100%.

**Thrashing.** Pushed past saturation without load shedding, the
system spends more cycles on overhead — context switching, garbage
collection, queue management — than on useful work. Throughput
collapses and error rates spike.

| Phase     | Throughput     | Latency             |
|-----------|----------------|---------------------|
| Linear    | Grows linearly | Low, flat           |
| Knee      | Slows          | Begins to climb     |
| Saturated | Plateaus       | Rises steeply       |
| Thrashing | Falls          | Timeouts or failure |

## What forces the bend

The transition from linear to saturation happens when one component
runs out of headroom. Common bottleneck classes:

- **CPU** — inefficient algorithms, heavy
  serialization/deserialization, cryptographic work
- **Memory** — leaks that exhaust the heap, or high allocation
  rates that trigger long garbage collection pauses
- **Network I/O** — bandwidth saturation, dropped packets, latency
  between internal services
- **Persistence** — row locks, missing indexes that force full
  table scans, exhausted connection pools

Whichever resource runs out first defines the ceiling. Removing it
shifts saturation to the next-most-constrained resource — never to
infinite capacity, just to a different bottleneck.

## Related

- [Performance testing](performance-testing.md) - Discovering the curve in CI

---

Return to [Testing](_index.md)
