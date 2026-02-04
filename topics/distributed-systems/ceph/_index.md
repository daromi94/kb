# Ceph

Ceph is an open-source distributed storage platform providing unified object,
block, and file storage from a single cluster. It uses the CRUSH algorithm for
decentralized data placement and is designed to be self-healing with no single
point of failure.

## Notes

- [Overview](overview.md) - Unified storage platform introduction
- [Storage interfaces](storage-interfaces.md) - RBD, RGW, and CephFS comparison
- [RADOS architecture](rados.md) - Core storage layer and daemons
- [CRUSH algorithm](crush-algorithm.md) - Decentralized data placement
- [Data placement](data-placement.md) - Pools and Placement Groups
- [Cluster operations](cluster-operations.md) - Maps, heartbeating, self-healing
- [Read/write paths](read-write-paths.md) - I/O flow through the system
- [Consistency](consistency.md) - CAP theorem analysis
- [Replication](replication.md) - Data protection and erasure coding
- [CephFS vs NFS](cephfs-vs-nfs.md) - When to use each
- [Architectural lessons](architectural-lessons.md) - Design patterns from Ceph

---

Return to [Distributed Systems](../_index.md)
