# Partitioning

Partitioning is the mechanism Cassandra uses to distribute data across a cluster
of nodes. It relies on consistent hashing to ensure that data is spread evenly
and that the cluster can scale horizontally without massive data migrations when
nodes are added or removed.

## The role of the partition key

When you define a table, the first part of your primary key is the partition
key. When a write occurs, Cassandra passes the value of this key into a
partitioner (a cryptographic hash function, typically Murmur3).

**The hash:** The partitioner turns the key (e.g., "User123") into a large
64-bit integer called a token.

**The destination:** This token determines which node in the cluster is
responsible for that specific piece of data.

## The token ring

Cassandra visualizes its cluster as a ring of possible token values (ranging
from $-2^{63}$ to $2^{63}-1$). Each physical node is assigned one or more ranges
of this ring.

**The clockwise rule:** When a partition key is hashed to a token, Cassandra
assigns the data to the node that owns the range containing that token.

**Scalability:** If you add a new node, it takes over a portion of the ranges
from its neighbors. Unlike traditional hashing (`hash % N`), which would require
re-mapping almost all data when $N$ changes, consistent hashing only requires
moving a small fraction of the data.

## Virtual nodes (vnodes)

In early versions of Cassandra, each physical node owned exactly one contiguous
segment of the ring. This led to two problems: it was hard to balance load
across different hardware, and if a node failed, only its immediate neighbor
took the extra traffic.

To solve this, Cassandra uses vnodes.

- Instead of one big segment, a physical node is assigned many small,
  non-contiguous token ranges (vnodes) across the ring.
- **Load balancing:** If one physical node is more powerful, you can assign it
  more vnodes.
- **Faster recovery:** If a node fails, its data is spread across many different
  ranges. This means every other node in the cluster helps rebuild the lost
  data, rather than putting the entire burden on a single neighbor.

## Why partitioning matters for performance

Partitioning dictates data locality. All rows that share the same partition key
are stored together in a single wide row on the same physical node.

| Feature             | Impact                                                          |
|---------------------|-----------------------------------------------------------------|
| **Efficient reads** | With the partition key, the coordinator contacts one node       |
| **Hot spots**       | Low-cardinality keys cause uneven distribution (hot partitions) |
| **Clustering**      | Within a partition, data is sorted by clustering columns        |

---

Return to [Cassandra](_index.md)
