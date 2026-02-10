# Cassandra fault tolerance

In Cassandra, fault tolerance is the ability of the system to continue operating
and serving data correctly even when nodes, racks, or entire data centers fail.
Because Cassandra is a masterless distributed system, it is designed to handle
hardware failure as an expected event rather than a catastrophe.

Fault tolerance is achieved through the combination of data redundancy,
decentralization, and self-healing mechanisms.

## No single point of failure

The most fundamental aspect of Cassandra's fault tolerance is its peer-to-peer
architecture.

**Masterless:** There is no leader node that manages the cluster. In a
leader-based system (like standard MySQL or MongoDB), if the leader fails, the
cluster is effectively dead until a new leader is elected.

**Redundant roles:** Every node can act as a coordinator for any query. If any
specific node fails, the client driver simply connects to a different node, and
operations continue without interruption.

## Data redundancy (replication)

Cassandra ensures that your data isn't lost when a disk or server fails by
keeping multiple copies (replicas) of every row.

**Replication factor (RF):** If $RF=3$, your data exists on three separate
nodes.

**Rack and DC awareness:** Using `NetworkTopologyStrategy`, Cassandra ensures
that replicas are not all on the same physical rack. It intelligently places
copies across different power supplies and network switches. Even if an entire
rack goes offline, the other two replicas in different racks stay available.

## Tunable availability (consistency levels)

Cassandra allows you to decide how much failure you can tolerate on a per-query
basis.

**QUORUM consistency:** If you have $RF=3$ and use `QUORUM`, you only need 2 out
of 3 replicas to be alive to succeed. This means the system can tolerate the
complete failure of any one node without the application ever seeing an error.

**Lowering the bar:** If you use `LOCAL_ONE`, you only need a single replica to
be alive. This provides higher availability during massive outages but carries a
higher risk of reading stale data.

## Self-healing mechanisms

When nodes fail and eventually return, Cassandra has built-in protocols to
synchronize the missed data and restore the cluster to full health.

### Hinted handoff

If a node is down during a write, the coordinator stores a hint (a temporary
note) on its own local disk. As soon as the failed node comes back online, the
coordinator hands off the missed updates to it.

### Read repair

If a read request finds that one replica has older data than the others (based
on the write timestamp), Cassandra returns the newest version to the user and
immediately updates the lagging replica in the background.

### Anti-entropy repair (manual)

Using `nodetool repair`, the system uses Merkle trees (hash trees) to compare
all data across replicas. This is a deep clean that ensures every bit of data is
identical across all copies, catching any inconsistencies that hinted handoff or
read repair might have missed.

## Summary of fault tolerance levels

| Failure type            | How Cassandra handles it                                              |
|-------------------------|-----------------------------------------------------------------------|
| **Disk failure**        | The node stops; replicas on other nodes serve the data                |
| **Node failure**        | Gossip detects the failure; hinted handoff stores missed writes       |
| **Rack failure**        | NetworkTopologyStrategy ensures replicas exist in other racks         |
| **Data center failure** | Cross-DC replication allows traffic to failover to a different region |

## Related

- [Replication](replication.md) - How data redundancy is configured
- [Hinted handoff](hinted-handoff.md) - Store-and-forward writes in depth
- [Anti-entropy](anti-entropy.md) - Read repair and Merkle tree repair in depth
- [Consistency](consistency.md) - Trade-offs between availability and consistency
- [Gossip](gossip.md) - How failures are detected

---

Return to [Cassandra](_index.md)
