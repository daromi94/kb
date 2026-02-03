# Cassandra primary key

In Cassandra, the primary key is the most critical part of your table schema. It
does more than ensure uniqueness; it dictates how data is distributed across the
cluster (partitioning) and how it is physically stored on disk (sorting).

A primary key is composed of two parts: the **partition key** and the
**clustering columns**.

## Partition key

The first component of the primary key. Its purpose is to determine data
locality.

**How it works:** When you write data, Cassandra takes the value of the
partition key and runs it through a hash function (usually Murmur3). The
resulting hash tells Cassandra which node in the ring should store that data.

**The wide row:** All rows that share the exact same partition key are stored
together in a single logical structure called a partition.

**Performance:** Queries that include the partition key are fast because the
coordinator node knows exactly which server to contact. Without it, the database
must perform a full cluster scan, which is a major performance antipattern.

## Clustering columns

Any columns defined in the primary key after the partition key. These determine
the on-disk sorting of data within a partition.

**How it works:** While the partition key finds the node, the clustering columns
determine the physical order of rows inside that partition. By default, they are
stored in ascending order, though this can be configured.

**Range queries:** Because data is physically sorted, you can perform highly
efficient range queries (using `>`, `<`, `BETWEEN`) on clustering columns.

**Storage:** This allows Cassandra to behave like a sorted map. If you store
logs with `user_id` as the partition key and `timestamp` as the clustering
column, all logs for one user are stored sequentially on disk, sorted by time.

## Syntax examples

### Simple primary key

The `id` is both the primary key and the partition key. There are no clustering
columns.

```cql
CREATE TABLE users (
    id   uuid PRIMARY KEY,
    name text
);
```

### Composite primary key

`user_id` is the partition key and `posted_at` is the clustering column.

```cql
CREATE TABLE posts_by_user (
    user_id   uuid,
    posted_at timestamp,
    content   text,
    PRIMARY KEY (user_id, posted_at)
);
```

### Composite partition key

Multiple columns grouped into the partition key using extra parentheses. Useful
when a single column doesn't have enough cardinality to distribute data evenly.
Here, `(lon, lat)` is the partition key and `captured_at` is the clustering
column.

```cql
CREATE TABLE weather_data (
    lon         int,
    lat         int,
    captured_at timestamp,
    temperature float,
    PRIMARY KEY ((lon, lat), captured_at)
);
```

## Summary

| Component             | Responsibility       | Performance benefit                       |
|-----------------------|----------------------|-------------------------------------------|
| **Partition key**     | Cluster distribution | Fast node lookups; avoids cluster scans   |
| **Clustering column** | Local sorting        | Fast range scans; efficient data grouping |

## Related

- [Partitioning](partitioning.md) - How data is distributed across the cluster
- [Consistent hashing](consistent-hashing.md) - The algorithm behind partition placement
- [Data modeling tips](data-modeling-tips.md) - Best practices for key design

---

Return to [Cassandra](_index.md)
