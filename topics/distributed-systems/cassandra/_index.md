# Cassandra

Distributed NoSQL database combining Amazon Dynamo's distribution design with
Google Bigtable's data model.

## Notes

- [Overview](overview.md) - Architecture principles, the ring, and use cases
- [Data model](data-model.md) - Structural hierarchy from keyspace to column
- [Primary key](primary-key.md) - Partition key and clustering columns
- [Consistent hashing](consistent-hashing.md) - Hash ring and virtual nodes
- [Partitioning](partitioning.md) - Data distribution via token ring
- [Replication](replication.md) - RF, strategies, and anti-entropy
- [Consistency](consistency.md) - Tunable consistency levels and strong consistency formula
- [Query routing](query-routing.md) - Coordinator, snitch, and dispatch
- [Storage model](storage-model.md) - LSM-tree, SSTables, and compaction
- [LSM-tree](lsm-tree.md) - Log-structured merge-tree fundamentals
- [Bloom filters](bloom-filters.md) - Probabilistic read path optimization
- [Caching](caching.md) - Key, row, chunk, and counter caches
- [Compaction](compaction.md) - SSTable merge strategies and maintenance
- [Tombstones](tombstones.md) - Deletion markers and gc_grace_seconds
- [Topology](topology.md) - Nodes, racks, data centers, and the snitch
- [Snitch](snitch.md) - Static vs dynamic snitching and optimized reads
- [Gossip](gossip.md) - Peer-to-peer protocol for cluster awareness
- [Phi accrual failure detector](phi-accrual.md) - Probabilistic failure detection via gossip
- [Fault tolerance](fault-tolerance.md) - No SPOF and self-healing mechanisms
- [Hinted handoff](hinted-handoff.md) - Store-and-forward writes during node failures
- [Anti-entropy](anti-entropy.md) - Read repair and Merkle tree-based repair
- [Lightweight transactions](lightweight-transactions.md) - Paxos-based compare-and-set
- [Data modeling tips](data-modeling-tips.md) - Query-driven design best practices
- [Architectural lessons](architectural-lessons.md) - Broader principles from Cassandra's design

---

Return to [Distributed Systems](../_index.md)
