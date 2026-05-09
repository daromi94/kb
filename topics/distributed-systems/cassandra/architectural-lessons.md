# Architectural lessons

Cassandra's architecture embodies several lessons that have become industry
standards for building highly available, linearly scalable distributed
systems.

## Decentralization over hierarchy

Traditional leader/follower architectures create a bottleneck and a single
point of failure. Cassandra's peer-to-peer model makes every node
functionally identical, eliminating the complex election phase required when
a leader dies. The system handles requests as long as any node is reachable.

## Tunable consistency

Rather than treating the CAP theorem as a static choice, Cassandra exposes
consistency as a per-query dial. Session tokens can prioritize speed over
accuracy while financial balances demand strict correctness — both on the
same cluster. The formula $W + R > RF$ achieves strong consistency on top of
an eventually consistent foundation through mathematical overlap of read and
write sets.

## Query-driven data modeling

Relational modeling starts with entities and normalizes to eliminate
duplication. Cassandra inverts this: start with queries, then design tables
to satisfy each access pattern in a single partition read. Denormalization
and data duplication are first-class strategies. Disk space is cheap;
cross-node joins are not.

## Consistent hashing for elastic scaling

Adding or removing nodes moves only $1/N$ of the data rather than
reshuffling everything. Virtual nodes spread each physical node across many
ring segments, so failure load is absorbed by the entire cluster rather than
a single neighbor. The result is near-linear horizontal scaling with minimal
disruption.

## Append-only storage

Using LSM-trees instead of B-trees reframes disk I/O. By treating the disk
as a log (commit log + SSTables) and never updating data in place, writes
become sequential and fast. This pattern now underpins high-performance
engines like RocksDB and storage layers in stream processors.

## Immutability simplifies concurrency

SSTables are never modified after being written. This removes the need for
distributed locks — one of the most expensive coordination primitives.
Deletes are handled through tombstones rather than in-place erasure. The
result is high write throughput without row-level locking. The same insight
drives event sourcing and append-only log architectures.

## Probabilistic over binary decisions

Two core components rely on probability rather than certainty. Bloom filters
give a fast "definitely not" or "maybe" answer to avoid unnecessary disk
seeks. The phi accrual failure detector replaces fixed-timeout heartbeats
with a continuous suspicion score that adapts to each connection's baseline,
eliminating the false-positive flapping that plagues binary approaches.

## Gossip for discovery

In large, dynamic clusters, maintaining a central node registry is fragile.
Epidemic (gossip) protocols make the cluster self-healing and
self-discovering. A three-way handshake exchanges only deltas, keeping
bandwidth low while propagating state changes across a 1,000-node cluster
in seconds.

## Timestamp-based conflict resolution

Rather than acquiring distributed locks for writes, Cassandra attaches a
microsecond timestamp to every cell. Concurrent updates to the same data
resolve through last-write-wins: the highest timestamp survives. This trades
deterministic ordering for lock-free writes at any scale.

## Design for failure

Rather than optimizing for the happy path, Cassandra assumes nodes will
fail. A layered recovery model handles progressively longer outages: hinted
handoff covers seconds to hours, read repair fixes hot data on every query,
and Merkle tree repair synchronizes cold data across the full dataset. The
system converges without human intervention.

## RDBMS vs distributed thinking

| Traditional RDBMS          | Distributed (Cassandra)         |
|----------------------------|---------------------------------|
| Normalize to save space    | Denormalize to save I/O         |
| Model entities, then query | Model queries, then store       |
| Leader node handles logic  | Peer nodes share all logic      |
| Lock rows during updates   | Timestamps and tombstones       |
| Fixed heartbeat timeouts   | Probabilistic failure detection |
| Strict ACID compliance     | Tunable consistency (BASE)      |

---

Return to [Cassandra](_index.md)
