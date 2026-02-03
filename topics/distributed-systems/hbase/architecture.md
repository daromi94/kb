# HBase architecture

HBase uses a master/slave architecture with strong consistency guarantees.
The system separates coordination, request handling, and storage into distinct
layers.

## Components

```
+------------------+
|     HMaster      |  Coordination
+--------+---------+
         |
    +----+----+
    |         |
+---v---+ +---v---+
|  RS1  | |  RS2  |  Request handling
+---+---+ +---+---+
    |         |
+---v---------v---+
|      HDFS       |  Storage
+-----------------+
```

**HMaster (coordinator):** Assigns regions to RegionServers and handles
metadata changes like schema updates. Uses ZooKeeper to track cluster state.
Does not handle read/write requests directly.

**RegionServers (workers):** Handle actual read/write requests. Each server
manages multiple regions.

**HDFS (storage layer):** HBase does not store data on local filesystems. It
sits on top of HDFS, which provides fault tolerance and data replication
(typically 3x).

**ZooKeeper:** Tracks cluster state, detects server failures, and prevents
split-brain scenarios.

## Regions

A **region** is a contiguous range of row keys (e.g., `UserA` to `UserG`). This
is HBase's unit of sharding.

- Each region is served by exactly one RegionServer at any time
- As tables grow, regions split automatically
- Regions are rebalanced across servers by the HMaster

This single-owner model enables strong consistency without distributed
coordination for individual operations.

## Comparison with peer-to-peer systems

| Aspect           | HBase (Master/Slave)      | Cassandra (Peer-to-Peer)         |
|------------------|---------------------------|----------------------------------|
| Coordination     | Centralized (HMaster)     | Decentralized (gossip)           |
| Region ownership | Single owner per region   | Multiple replicas, any can serve |
| Failure handling | Master reassigns regions  | Requests route around failures   |
| Complexity       | Simpler consistency model | More complex conflict resolution |

## Related

- [Consistency model](consistency-model.md) - How single-owner enables CP
- [Storage engine](storage-engine.md) - How data flows through the system
