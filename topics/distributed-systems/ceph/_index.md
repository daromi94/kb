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
- [Read and write paths](read-write-paths.md) - I/O flow through the system
- [Consistency model](consistency.md) - CAP theorem analysis
- [Replication](replication.md) - Data protection and erasure coding
- [CephFS vs NFS](cephfs-vs-nfs.md) - When to use each
- [Architectural lessons](architectural-lessons.md) - Transferable design principles

---

Return to [Distributed systems](../_index.md)
