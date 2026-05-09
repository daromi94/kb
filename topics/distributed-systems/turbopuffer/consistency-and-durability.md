# Consistency and durability

The consistency model is built on writing the WAL to object storage
and searching both indexed and unindexed data on every query.

## Write-ahead log

Every write is durably committed to a WAL in S3 before the API
returns success. A write acknowledged with `200 OK` is guaranteed
to be in object storage.

- **Batching.** Each namespace commits one WAL entry per second.
  Concurrent writes are batched to amortize S3 `PUT` latency.
- **Throughput.** The append-only WAL design supports 10,000+ vectors
  per second per namespace.
- **Write latency.** The S3 roundtrip creates a ~285ms latency floor,
  which is the cost of durable writes without local disk.

If query nodes crash, they reconstruct state by replaying the WAL
from object storage.

## Consistency model

**Strong consistency (default).** Every query searches two sources:

1. The optimized SPFresh/BM25 index (fast path).
2. Unindexed WAL fragments (exhaustive scan).

By merging results from both, the system guarantees read-your-writes
semantics. A document written one millisecond ago appears in the
next query.

**Eventual consistency (opt-in).** Skips the S3 metadata roundtrip
to check for new WAL entries. Drops query latency to sub-10ms but
data may be up to 60 seconds stale. Useful when freshness is less
important than speed.

## ACID properties

| Property    | Behavior                              |
|-------------|---------------------------------------|
| Atomicity   | Batch upserts are all-or-nothing      |
| Consistency | Strong by default, eventual opt-in    |
| Durability  | Committed to S3 before acknowledgment |
| Isolation   | Varies by operation (see below)       |

## Isolation levels

| Operation              | Isolation Level | Mechanism                                                |
|------------------------|-----------------|----------------------------------------------------------|
| Conditional writes     | Serializable    | Evaluate condition + write in one atomic step            |
| Patch/delete by filter | Read Committed  | Two-phase: find matching IDs, then re-evaluate and apply |

Conditional writes (e.g., "update only if `version < 5`") prevent
lost updates without requiring general-purpose transactions. Filter
operations may miss documents inserted between the find and apply
phases.

## CAP theorem stance

Turbopuffer chooses consistency over availability (CP). If object
storage is unreachable, the system returns errors rather than serving
potentially stale or incorrect data. The single stateful dependency on
object storage eliminates the consensus problems of multi-node
stateful architectures.

---

Return to [Turbopuffer](_index.md)
