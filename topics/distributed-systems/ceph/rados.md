# RADOS Architecture

The core of every Ceph cluster is **RADOS** (Reliable Autonomic Distributed
Object Store). Every piece of data---whether from a virtual disk, S3 bucket, or
file system---is stored as an object within this layer.

## Core Daemons

### OSD (Object Storage Daemon)

The primary worker. Stores data on behalf of clients, handles replication,
recovery, and rebalancing. Also provides heartbeat information to Monitors.
Generally one OSD daemon per physical disk.

### Monitor (MON)

Maintains the "master maps" of cluster state:

- **OSD Map:** Which disks are up/down and in/out
- **Monitor Map:** Which monitors are in quorum
- **PG Map:** Placement Group states
- **CRUSH Map:** Physical hierarchy of the data center

Monitors do not store user data. They provide consensus via Paxos for cluster
coordination. High availability requires an odd number (3 or 5).

### Manager (MGR)

Tracks runtime metrics (storage utilization, performance counters). Hosts the
Ceph Dashboard and orchestration modules like `cephadm`.

### Metadata Server (MDS)

Only required for CephFS. Stores file system metadata (directory structures,
permissions) so data can be retrieved directly from OSDs.

## Storage Backend: BlueStore

In modern Ceph releases, **BlueStore** is the default OSD backend. Unlike older
implementations that stored data on top of a Linux file system (XFS), BlueStore
manages the raw block device directly.

Benefits:

- Reduced overhead
- No double-journaling issues
- Internal RocksDB instance for metadata
- Write-Ahead Log (WAL) for durability

## Architecture Diagram

```
+------------------+  +------------------+  +------------------+
|   Block (RBD)    |  |  Object (RGW)    |  |   File (CephFS)  |
+------------------+  +------------------+  +------------------+
         |                    |                     |
         +--------------------+---------------------+
                              |
                    +------------------+
                    |      RADOS       |
                    +------------------+
                              |
         +--------------------+---------------------+
         |                    |                     |
    +--------+           +--------+            +--------+
    |  OSD   |           |  OSD   |            |  OSD   |
    +--------+           +--------+            +--------+
```

## Related

- [CRUSH algorithm](crush-algorithm.md) - How data placement is calculated
- [Data placement](data-placement.md) - Pools and Placement Groups
- [Cluster operations](cluster-operations.md) - How daemons coordinate

---

Return to [Ceph](_index.md)
