# Cassandra data model

In Cassandra, the data model is designed to support distributed scale by
prioritizing how data is physically laid out on disk and across the network.
While it uses SQL-like syntax (CQL), it is structurally a distributed
multidimensional map or partitioned row store.

The most critical distinction from relational modeling: **model for your
queries**, not for your entities.

## Structural hierarchy

1. **Keyspace:** The outermost container (analogous to a database in MySQL).
   Replication strategy and replication factor are defined here.

2. **Table:** A collection of rows. Unlike relational databases, tables are
   designed to be "wide," handling billions of rows and thousands of columns.

3. **Partition:** The unit of data distribution. A table is divided into
   partitions based on the hash of the partition key. All data in a single
   partition is stored together on the same nodes.

4. **Row:** A collection of columns identified by a unique primary key within a
   partition.

5. **Column:** The smallest unit of data, consisting of a name, a value, and a
   client-side timestamp.

## Key modeling concepts

### Denormalization

Cassandra does not support joins. If you need to view data in two different ways
(e.g., "users by email" and "users by username"), you create two separate
tables. Disk space is cheap; CPU and network overhead for joins are expensive.

### Last write wins (LWW)

If two nodes receive an update for the same cell simultaneously, Cassandra
compares the timestamps attached to the columns. The one with the highest
microsecond timestamp is kept.

### Tombstones

Deletions are not immediate erasures. Instead, Cassandra writes a tombstone, a
special marker indicating the data is deleted. During compaction, the system
reconciles these markers and eventually removes the old data.

## Comparison with relational models

| Feature         | Relational (RDBMS)        | Apache Cassandra                |
|-----------------|---------------------------|---------------------------------|
| **Joins**       | Supported (normalization) | Not supported (denormalization) |
| **Schema**      | Rigid                     | Flexible / wide column          |
| **Querying**    | Flexible (declarative)    | Restrictive (query-driven)      |
| **Consistency** | ACID                      | Tunable (eventual to strong)    |
| **Scaling**     | Vertical (bigger servers) | Horizontal (more nodes)         |

## Related

- [Primary key](primary-key.md) - Partition keys and clustering columns
- [Data modeling tips](data-modeling-tips.md) - Best practices for schema design
- [Storage model](storage-model.md) - How data is stored on disk

---

Return to [Cassandra](_index.md)
