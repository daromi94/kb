# Replication

Replication copies the same data across multiple nodes. Its primary
purpose is **availability and fault tolerance** — the system remains
operational and data remains durable when individual components fail.

## Synchronous vs asynchronous

**Synchronous:** The leader waits for all (or a majority of) replicas to
acknowledge a write before confirming success to the client. Prioritizes
consistency at the cost of latency.

**Asynchronous:** The leader acknowledges immediately after storing locally
and sends data to replicas in the background. Prioritizes performance but
risks data loss if the leader crashes before replicas receive the update.

## Replication strategies

**Leader-follower.** One node handles all writes and propagates changes to
followers. Followers serve read-only traffic to offload the leader.

**Multi-leader.** Multiple nodes accept writes and synchronize with each
other. Common across geographic regions to reduce latency, but introduces
conflict resolution complexity.

**Leaderless (quorum-based).** Any node accepts writes. The system relies
on a quorum of nodes agreeing on data to ensure consistency. Used by
Cassandra and DynamoDB.

## Key patterns

### High-water mark

An index in the log indicating the last entry safely replicated across a
majority of the cluster. Clients only read up to this point to avoid seeing
uncommitted data that might vanish if a leader fails.

### Quorum

The minimum number of nodes that must participate in an operation for it to
succeed. With $n$ replicas, write quorum $W$ and read quorum $R$ must
satisfy:

$$W + R > n$$

This guarantees the read set and write set always overlap, so at least one
node in a read request holds the most recent data.

### Reconciliation and anti-entropy

When a node recovers from downtime, it will be stale. Strategies to bring
it up to date:

- **Read repair** — The system compares versions during a read and updates
  the stale node on the fly
- **Hinted handoff** — Other nodes temporarily store writes meant for the
  downed node and replay them once it returns
- **Merkle trees** — Hash-based structures that quickly identify which
  pieces of data are out of sync without transferring the entire dataset

## Why replicate

- **Disaster recovery** — A replica in another location keeps the service
  alive if a data center loses power
- **Reduced latency** — Placing replicas closer to users (Europe and US)
  speeds up access
- **Read scalability** — Distributing reads across followers handles more
  traffic than a single node

## Related

- [Partitioning](partitioning.md) - Splits data for scale; often combined
  with replication for fault tolerance
- [CAP theorem](cap-theorem.md) - Consistency vs availability trade-offs
  during network partitions
- [Write-ahead log](write-ahead-log.md) - The log that replication
  propagates between nodes

---

Return to [Concepts](_index.md)
