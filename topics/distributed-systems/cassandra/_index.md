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
- [Gossip](gossip.md) - Peer-to-peer protocol for cluster awareness
- [Fault tolerance](fault-tolerance.md) - No SPOF and self-healing mechanisms
- [Data modeling tips](data-modeling-tips.md) - Query-driven design best practices
