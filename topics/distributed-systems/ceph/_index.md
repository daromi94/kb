# Ceph

Ceph is an open-source distributed storage platform providing unified object,
block, and file storage from a single cluster. It uses the CRUSH algorithm for
decentralized data placement and is designed to be self-healing with no single
point of failure.

## Notes

- [Overview](overview.md) - Unified storage platform
- [Storage interfaces](storage-interfaces.md) - Block, object, and file APIs
- [RADOS architecture](rados.md) - Core storage layer and daemons
- [CRUSH algorithm](crush-algorithm.md) - Decentralized data placement
- [Data placement](data-placement.md) - Logical partitioning layers
- [Cluster operations](cluster-operations.md) - Coordination and self-healing
- [Replication](replication.md) - Data durability mechanisms
- [Read and write paths](read-write-paths.md) - I/O flow through the system
- [Consistency model](consistency.md) - CAP theorem analysis
- [CephFS vs NFS](cephfs-vs-nfs.md) - When to use each
- [Architectural lessons](architectural-lessons.md) - Transferable design principles

---

Return to [Distributed systems](../_index.md)
