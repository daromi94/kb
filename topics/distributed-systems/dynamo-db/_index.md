# DynamoDB

Fully managed NoSQL database designed for single-digit millisecond
latency at any scale.

## Notes

- [Architecture](architecture.md) - Microservice decomposition, request path, and autoadmin control plane
- [Data model](data-model.md) - Table structure, primary keys, and partition placement
- [Partitioning and replication](partitioning-and-replication.md) - Partition layout, replication groups, and
  Multi-Paxos leader election
- [Replica types](replica-types.md) - Storage replicas vs. log replicas for quorum healing
- [Transactions](transactions.md) - ACID guarantees via two-phase commit across partitions
- [Performance](performance.md) - Low-latency architecture and admission control
- [Operational lessons](operational-lessons.md) - Principles from a decade at scale

---

Return to [Distributed systems](../_index.md)
