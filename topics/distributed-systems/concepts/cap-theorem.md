# CAP Theorem

The CAP theorem (Brewer's theorem) states that a distributed data store
cannot simultaneously guarantee more than two of: **consistency**,
**availability**, and **partition tolerance**.

## The three guarantees

**Consistency (C):** Every read receives the most recent write or an error.
Once data is written to one node, it is instantly visible across all nodes.

**Availability (A):** Every request receives a non-error response, without
guaranteeing it reflects the most recent write. The system stays
operational even when some nodes are down.

**Partition tolerance (P):** The system continues operating despite
messages being dropped or delayed between nodes (a network partition).

## The real choice: CP vs AP

Network partitions are inevitable in distributed systems, so partition
tolerance is not optional. The practical decision is how the system behaves
when a partition occurs.

### CP (consistency + partition tolerance)

The system stops accepting writes or returns errors if it cannot guarantee
data is up to date. Correctness over availability.

- Nodes return errors or time out when they cannot communicate
- Suits banking systems, distributed locks — wrong data is worse than no
  data
- Examples: MongoDB (certain configurations), etcd, ZooKeeper

### AP (availability + partition tolerance)

The system continues responding even when nodes cannot communicate.
Uptime over correctness.

- Nodes serve their local version of data, even if stale; conflict
  resolution syncs data once the partition heals
- Suits social media feeds, shopping carts — stale data is better than a
  500 error
- Examples: Cassandra, DynamoDB, CouchDB

## Partition behavior walkthrough

1. Node A and Node B are separated by a network failure
2. A user writes new data to Node A
3. **CP choice:** Node A refuses the write because it cannot inform Node B;
   the system stays consistent but becomes unavailable
4. **AP choice:** Node A accepts the write; Node B still has old data; the
   system stays available but reads from Node B return stale results

## PACELC: beyond CAP

The PACELC theorem extends CAP to describe behavior when the network is
healthy:

- **P**artition → trade off **A**vailability vs **C**onsistency
- **E**lse → trade off **L**atency vs **C**onsistency

This captures a common reality: even without failures, a system may choose
weaker consistency to achieve lower latency.

## Related

- [Replication](replication.md) - The mechanism through which consistency
  and availability trade-offs manifest
- [Partitioning](partitioning.md) - Data distribution that network
  partitions can disrupt

---

Return to [Concepts](_index.md)
