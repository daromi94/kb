# Latency-throughput tradeoff

Low latency requires empty queues so each request is served immediately.
High throughput requires full queues so workers never idle. A system
optimized for one sacrifices the other.

## Why they conflict

A worker is either idle or busy. Idle workers serve the next request
instantly but waste capacity. Busy workers maximize utilization but
force new arrivals to wait in line.

Queuing theory quantifies this: response time stays flat
until ~70% utilization, then climbs steeply toward infinity as
utilization approaches 100%. You cannot run a system at full
utilization and expect low latency.

## Batching: the canonical mechanism

Batching amortizes fixed per-operation costs — network round-trips,
disk seeks, lock acquisitions — across multiple operations. Each
item waits for the batch to fill, increasing its latency, but the
cost per operation drops.

| System          | Mechanism                  | What it trades              |
|-----------------|----------------------------|-----------------------------|
| Kafka producer  | `linger.ms` + `batch.size` | Send delay for fewer RPCs   |
| TCP Nagle       | Buffer small segments      | Packet delay for efficiency |
| Database INSERT | Multi-row batches          | Query delay for fewer txns  |

Every buffer in a system is a hidden waiting room where individual
items trade their latency for the system's throughput.

## The asymmetry

Throughput scales with money: add servers, cables, cores. Latency is
bounded by physics — light in fiber travels at 200,000 km/s, already
two-thirds of its theoretical maximum.

Since latency cannot be bought away, systems hide it with caching,
prefetching, and replication.

## The design choice

| Target          | Strategy                   | Consequence                    |
|-----------------|----------------------------|--------------------------------|
| Low latency     | No queuing, idle resources | Users fast, machines underused |
| High throughput | Pipelining, batching       | Machines busy, users wait      |

---

Return to [Latency](_index.md)
