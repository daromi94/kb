# HBase storage engine

HBase uses a Log-Structured Merge (LSM) tree for storage, optimizing for write
throughput while maintaining good read performance through background
compaction.

## Write path

```
+-------------------+
|   Client Write    |
+---------+---------+
          |
          v
+---------+---------+
|   WAL (on HDFS)   |  1. Append for durability
+---------+---------+
          |
          v
+---------+---------+
|     MemStore      |  2. In-memory buffer
+---------+---------+
          | (flush when full)
          v
+---------+---------+
|      HFile        |  3. Immutable on-disk file
+-------------------+
```

**WAL (Write-Ahead Log):** Data is first appended to a log file on HDFS for
durability. If a RegionServer crashes, the WAL replays to recover uncommitted
writes.

**MemStore:** Data is then written to an in-memory sorted buffer. Each column
family has its own MemStore.

**HFile:** When the MemStore fills up (configurable threshold), it flushes to
disk as an immutable HFile. HFiles are never modified after creation.

## Compaction

Since HFiles are immutable, updates and deletes create new entries rather than
modifying existing ones. Over time, reading a single row might require scanning
many HFiles.

**Minor compaction:** Merges a small number of HFiles into a larger one.
Reduces file count without major I/O.

**Major compaction:** Merges all HFiles for a region into one, purging deleted
entries (tombstones) and expired versions. More I/O intensive but reclaims
space and optimizes reads.

## HBase vs Cassandra storage

Both use LSM trees but differ in where data lives:

| Aspect       | HBase                              | Cassandra                        |
|--------------|------------------------------------|----------------------------------|
| Filesystem   | HDFS (distributed)                 | Local FS (ext4/XFS)              |
| Partitioning | Range (keys sorted globally)       | Consistent hashing (keys hashed) |
| Replication  | Handled by HDFS DataNodes          | Handled by Cassandra itself      |
| I/O pattern  | Network-bound (writing to HDFS)    | Disk-bound (local append)        |
| Range scans  | Efficient (adjacent keys together) | Inefficient (keys scattered)     |

**Cassandra equivalents:**

- WAL → Commit Log
- MemStore → Memtable
- HFile → SSTable (Sorted String Table)

Cassandra's SSTables include additional files: `Data.db` (data), `Index.db`
(partition offsets), and `Filter.db` (Bloom filter for negative lookups).

## Compaction strategies (Cassandra)

Cassandra offers pluggable compaction strategies:

- **SizeTieredCompaction:** Default. Merges similarly-sized SSTables. Good for
  write-heavy workloads.
- **LeveledCompaction:** Organizes SSTables into levels. Keeps read latency
  predictable. Better for read-heavy workloads.

## Related

- [Data model](data-model.md) - Logical structure that maps to this storage
- [Netty I/O](netty-io.md) - How writes reach HDFS efficiently
