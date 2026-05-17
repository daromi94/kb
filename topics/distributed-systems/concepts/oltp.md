# OLTP

Online Transaction Processing (OLTP) is the workload class for
high-throughput, low-latency mutation of state under ACID
guarantees. Systems of record — financial ledgers, inventory
tracking, reservation systems — sit on OLTP engines because every
operation must commit, durably, in milliseconds or less.

## Workload characteristics

- **Granularity:** Point queries and targeted updates dominate.
  Transactions touch a narrow subset of records, not full-table scans.
- **Profile:** Write-heavy or a tightly interleaved read/write mix.
- **Concurrency:** Extreme. Thousands to millions of concurrent
  transactions compete for the same data structures.
- **Latency:** Microseconds to low milliseconds per transaction.
  Slower than that and the system blocks money or goods moving in
  the real world.

## ACID guarantees

All four are required. Drop any one and the system silently
corrupts state under concurrent load or crashes.

| Guarantee   | What it enforces                                   |
|-------------|----------------------------------------------------|
| Atomicity   | A transaction commits or aborts as a unit          |
| Consistency | Every commit preserves all integrity constraints   |
| Isolation   | Concurrent transactions appear to run sequentially |
| Durability  | Once acknowledged, a commit survives any crash     |

OLTP demands the strongest isolation level: strict serializability.

## Strict serializability

Strict serializability is the highest isolation level. It requires
that concurrent execution be functionally identical to some
sequential execution that also respects real-time order. Two
transactions that overlap in wall-clock time must appear to commit
in an order consistent with when they actually happened.

This is the only isolation level safe for ledgers, inventory, and
other systems where state must reflect physical reality. Weaker
levels — snapshot isolation, read committed, eventual consistency —
permit lost updates, write skew, or dirty reads that corrupt the
record.

## Power-law contention

Transaction distribution is not uniform. A small fraction of records
attracts a large fraction of traffic: a central clearing account, a
top-selling product, a frequently visited user. These hot keys become
contended bottlenecks where thousands of concurrent transactions
queue against the same record.

Power-law contention is why horizontal sharding fails to scale OLTP
throughput. Adding shards does not help when the bottleneck is a
single record that must serialize updates to preserve isolation.

## Safety is not negotiable

In OLTP, correctness comes before throughput. Wrong answers cost
more than the latency saved producing them. Preserve strict
serializability and ACID first; optimize after.

---

Return to [Concepts](_index.md)
