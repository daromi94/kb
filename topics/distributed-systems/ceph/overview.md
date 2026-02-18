# Ceph overview

Ceph is an open-source, distributed storage platform providing object, block,
and file storage from a single, unified cluster. It is architected to be
self-healing and self-managing, with no single point of failure, capable of
scaling from a few nodes to thousands of servers.

## Unified Storage

Unlike traditional systems that require separate infrastructure for different
storage types, Ceph runs all three interfaces on top of the same underlying
**RADOS** (Reliable Autonomic Distributed Object Store) cluster:

| Interface     | Protocol          | Use Case                              |
|---------------|-------------------|---------------------------------------|
| Block (RBD)   | Kernel/librbd     | VM disks, Kubernetes PVs              |
| Object (RGW)  | S3/Swift REST API | Backups, media files, data lakes      |
| File (CephFS) | POSIX mount       | Shared directories, HPC scratch space |

## Key Characteristics

**Scalability:** Performance and capacity scale linearly by adding commodity
hardware. No central controller bottleneck.

**Durability:** Data protected via replication (multiple copies) or erasure
coding (RAID-like parity across nodes).

**Self-Healing:** When a disk or node fails, the cluster automatically
redistributes data to restore the configured replica count.

**Hardware Agnostic:** Runs on standard x86 servers, avoiding vendor lock-in
with proprietary storage arrays.

## The CRUSH Innovation

The defining technical feature is the **CRUSH** (Controlled Replication Under
Scalable Hashing) algorithm. Unlike traditional storage that uses a central
lookup table to find files, Ceph calculates data locations on the fly. Clients
use CRUSH to determine which OSDs hold data, eliminating the central bottleneck.

## Related

- [Storage interfaces](storage-interfaces.md) - The three access methods
- [RADOS architecture](rados.md) - Core storage layer and daemons
- [CRUSH algorithm](crush-algorithm.md) - How data placement is calculated

---

Return to [Ceph](_index.md)
