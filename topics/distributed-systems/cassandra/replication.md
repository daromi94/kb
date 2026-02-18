# Replication

In Cassandra, replication is the mechanism that ensures high availability and
durability. While partitioning decides which node is the primary owner of data,
replication determines how many additional copies exist and where they are
placed across the cluster.

## Replication factor (RF)

Replication is configured at the keyspace level using the replication factor.
The RF is the total number of nodes that will store a copy of a specific row.

- **RF=1:** Only one copy exists. If that node fails, the data is lost.
- **RF=3:** (Industry standard) Three nodes store the data. The system can lose
  one node and still maintain quorum (majority) consistency.

## Replication strategies

Cassandra uses a strategy to decide which specific nodes in the ring will act as
replicas.

### SimpleStrategy

Used for single data center deployments. It picks the first replica based on the
partitioner's token and then places subsequent replicas on the next nodes moving
clockwise around the ring.

### NetworkTopologyStrategy

The preferred strategy for production. It is datacenter-aware and rack-aware.

**Multi-DC:** It allows you to set different RFs for different regions (e.g.,
`US-East: 3, US-West: 3`).

**Rack awareness:** It ensures that replicas are placed on different physical
racks. This prevents a single top-of-rack switch failure from making all copies
of your data unavailable.

## The role of the coordinator

When a client sends a write or read request, it connects to any node in the
cluster, which then acts as the coordinator.

1. **Identify replicas:** The coordinator uses the partition key and the
   replication strategy to find all $N$ nodes (where $N = RF$) that should own
   the data.
2. **Dispatch:** It sends the request to all $N$ replicas simultaneously.
3. **Consistency check:** The coordinator waits for a certain number of nodes to
   acknowledge the request based on the consistency level set by the client
   (e.g., `ONE`, `QUORUM`, `ALL`).

Even if the consistency level is set to `ONE`, the coordinator still attempts to
write to all replicas. The CL only dictates how many must succeed before the
coordinator tells the client the operation was successful.

## Anti-entropy mechanisms

Because replicas can go down or experience network partitions, Cassandra uses
several self-healing mechanisms to keep replicas in sync:

**Hinted handoff:** If a replica is down, the coordinator stores a hint (a
reminder) on its own disk. When the target node comes back online, the
coordinator delivers the missed update.

**Read repair:** When a read happens, the coordinator compares data from
multiple replicas. If it sees one is out of date, it immediately updates that
node with the latest version.

**Nodetool repair:** A manual background process that uses Merkle trees (hash
trees) to compare all data across replicas and synchronize any differences.

## Summary

| Feature         | Detail                                                         |
|-----------------|----------------------------------------------------------------|
| **Placement**   | Determined by the replication strategy (Simple vs. Network)    |
| **Redundancy**  | Controlled by the replication factor (RF)                      |
| **Consistency** | Tunable at request time via the consistency level (CL)         |
| **Durability**  | Achieved by distributing copies across different racks and DCs |

## Related

- [Consistency](consistency.md) - Tunable consistency levels
- [Hinted handoff](hinted-handoff.md) - Store-and-forward for missed writes
- [Anti-entropy](anti-entropy.md) - Read repair and Merkle tree repair
- [Fault tolerance](fault-tolerance.md) - How replication enables resilience
- [Query routing](query-routing.md) - How the coordinator works

---

Return to [Cassandra](_index.md)
