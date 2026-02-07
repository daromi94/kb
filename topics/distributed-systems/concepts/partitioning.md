# Partitioning

Partitioning (sharding) splits a large dataset into smaller chunks
distributed across multiple nodes. Its primary purpose is **scalability
and performance** — each node handles a different subset of the data,
spreading both storage and throughput across the cluster.

## Why partition

A single machine has physical limits on storage capacity and
read/write throughput. A system with 10 partitions can theoretically handle
10x the data and 10x the traffic of a single node.

**Write parallelism.** In a leader-follower setup every write funnels
through one node. Partitioning lets different writes land on different
nodes simultaneously, removing the single-leader bottleneck.

**Query performance.** The system only scans the partition where the data
resides rather than the full dataset, and complex aggregations can run in
parallel across partitions with a coordinator merging results.

**Blast radius.** If one node in a 10-node cluster fails, only that
partition's slice is offline. The remaining 90% continues serving
requests, and maintenance can happen per-partition without full downtime.

## Partitioning strategies

### Key-range partitioning

Data is sorted and contiguous key ranges are assigned to partitions (e.g.,
Partition 1 holds names A-G, Partition 2 holds H-N).

- **Pro:** Efficient range queries ("find all users with names starting
  with B")
- **Con:** Susceptible to hot spots if keys are unevenly distributed

### Hash partitioning

A hash function is applied to the key and the result determines the
partition.

- **Pro:** Distributes data evenly, preventing hot spots
- **Con:** Range queries are expensive because data is scattered randomly
  across partitions

## Hot spots and skew

A partition is **skewed** when it holds disproportionately more data or
receives more traffic. A social media app partitioned by user ID will
create a hot partition for a celebrity with millions of followers, even if
the rest of the cluster is idle.

## Partitioning and replication

|               | Replication                      | Partitioning                    |
|---------------|----------------------------------|---------------------------------|
| Goal          | Availability and safety          | Scalability and throughput      |
| Data strategy | Copy the same data to many nodes | Split data into disjoint pieces |
| On failure    | Other copies serve requests      | Only the affected slice is lost |

In production, these patterns are used together. A dataset is partitioned
for scale, then each partition is replicated for fault tolerance.

In a 3-node cluster with 2 partitions:

| Node   | Partition A | Partition B |
|--------|-------------|-------------|
| Node 1 | Leader      | Follower    |
| Node 2 | Follower    | Leader      |
| Node 3 | Follower    | Follower    |

## Operational concerns

**Request routing.** How does a client know which node holds its data?
Systems use a request router or a gossip protocol to maintain a map of
partitions to nodes.

**Rebalancing.** Adding a node requires moving some partitions from
existing nodes to the new one to balance load.

**Distributed joins.** Joining data across partitions on different machines
is slow and often avoided in distributed database design.

## Related

- [Replication](replication.md) - Copies partitions across nodes for fault
  tolerance
- [CAP theorem](cap-theorem.md) - Trade-offs that shape partition behavior
  during network splits

---

Return to [Concepts](_index.md)
