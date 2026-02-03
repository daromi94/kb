# Cassandra data modeling tips

In Cassandra, data modeling is the art of query-driven design. Unlike relational
databases where you model based on entity relationships (normalization), in
Cassandra you model specifically to satisfy your application's query patterns.

## Model for your queries, not your entities

The most common mistake is trying to create a "User" table and a "Post" table
and expecting to join them. Cassandra does not support joins.

**Technique:** List every query your application will perform (e.g., "find all
comments for a post," "find all posts by a user").

**Tip:** Create one table per query. If you need to see data in three different
ways, you will likely have three different tables, even if they contain the same
data.

## Denormalization is a virtue

In RDBMS, duplication is a code smell. In Cassandra, it is a requirement for
performance.

**Technique:** Duplicate data across tables to ensure that a single query can be
satisfied by reading from a single partition.

**Tip:** Don't be afraid of wide rows. Storing 1,000 comments in a single
partition under a `post_id` is significantly faster than fetching 1,000 separate
rows from different parts of a cluster.

## Minimize partition scans

A query is most efficient when it hits exactly one node. A query that hits every
node in the cluster (a scatter-gather query) will not scale.

**Technique:** Every query must include the partition key in the `WHERE` clause.

**Tip:** If you find yourself needing `ALLOW FILTERING`, your data model is
likely incorrect for that query. `ALLOW FILTERING` forces Cassandra to scan all
data in a partition (or the whole cluster) and filter it in memory, which is a
major performance bottleneck.

## Optimize with clustering columns

Clustering columns determine the physical sort order of your data on disk.

**Technique:** Use clustering columns to group data that you need to retrieve in
ranges.

**Tip:** If you are building a time-series application, use `timestamp` as a
clustering column. This allows you to perform highly efficient slice queries to
get the "last 10 records" or "all records between 2 PM and 4 PM."

## Control partition size (the hot partition problem)

While Cassandra can handle large partitions, a partition that grows into the
gigabytes can lead to high JVM garbage collection pressure and slow compactions.

**Technique:** Aim for partitions under 100MB and fewer than 100,000 rows per
partition.

**Tip:** Use bucketing to break up massive partitions. If you have millions of
logs for a single sensor, don't just use `sensor_id` as the partition key. Use
`(sensor_id, date)` so that each day's data resides in a fresh, manageable
partition.

## Avoid unbounded deletes

Frequent deletes create tombstones, which can degrade read performance as the
coordinator has to scan through dead data markers.

**Technique:** Instead of deleting data, consider using TTL (Time To Live) on
your columns.

**Tip:** If you must delete, try to delete an entire partition rather than
individual rows within a partition. Partition-level deletes are handled much
more efficiently during compaction.

## RDBMS vs. Cassandra modeling

| Feature           | Relational (RDBMS)        | Apache Cassandra            |
|-------------------|---------------------------|-----------------------------|
| **Data goal**     | Minimize duplication      | Minimize seek time          |
| **Joins**         | Core functionality        | None (handled at app level) |
| **Scaling**       | Vertical                  | Horizontal                  |
| **Relationships** | Foreign keys              | Denormalization / bucketing |
| **Write cost**    | Expensive (index updates) | Very cheap (sequential)     |

## Related

- [Primary key](primary-key.md) - Partition key and clustering column design
- [Partitioning](partitioning.md) - How data locality affects queries
- [Storage model](storage-model.md) - Why tombstones matter
