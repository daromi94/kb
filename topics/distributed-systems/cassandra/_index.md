# Cassandra

Distributed NoSQL database combining Amazon Dynamo's distribution design with
Google Bigtable's data model.

## Notes

- [Overview](overview.md) - Core architecture and purpose
- [Data model](data-model.md) - Distributed data structure
- [Primary key](primary-key.md) - Key design and data locality
- [Data modeling tips](data-modeling-tips.md) - Query-driven schema design
- [Topology](topology.md) - Cluster physical layout
- [Consistent hashing](consistent-hashing.md) - Token-based data distribution
- [Partitioning](partitioning.md) - Data distribution across nodes
- [Replication](replication.md) - Data redundancy and placement
- [Snitch](snitch.md) - Topology-aware routing
- [Gossip](gossip.md) - Peer-to-peer state propagation
- [Phi accrual failure detector](phi-accrual.md) - Probabilistic failure detection
- [Query routing](query-routing.md) - Request dispatch and coordination
- [Consistency](consistency.md) - Tunable consistency trade-offs
- [Lightweight transactions](lightweight-transactions.md) - Paxos-based compare-and-set
- [Storage model](storage-model.md) - On-disk storage architecture
- [LSM-tree](lsm-tree.md) - Append-only storage fundamentals
- [Compaction](compaction.md) - Background storage maintenance
- [Tombstones](tombstones.md) - Distributed deletion mechanics
- [Bloom filters](bloom-filters.md) - Probabilistic read optimization
- [Caching](caching.md) - In-memory read optimization
- [Fault tolerance](fault-tolerance.md) - Self-healing and resilience
- [Hinted handoff](hinted-handoff.md) - Store-and-forward during failures
- [Anti-entropy](anti-entropy.md) - Replica synchronization
- [Architectural lessons](architectural-lessons.md) - Broader design principles

---

Return to [Distributed systems](../_index.md)
