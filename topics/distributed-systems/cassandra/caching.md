# Caching

Cassandra uses a multi-layered caching architecture to reduce disk I/O and
offset the read penalty inherent in LSM-tree storage. By keeping frequently
accessed metadata and data in memory, reads can be served at sub-millisecond
speeds.

## Key cache (on-heap)

Stores the disk byte offset for partition keys. Without it, Cassandra must
consult the partition summary and partition index on disk to locate a row in
an SSTable. With it, the coordinator jumps directly to the exact byte offset.

Enabled by default. Low memory overhead relative to its performance benefit.

## Row cache (off-heap)

Stores the entire contents of a row (all columns and values). Provides the
fastest possible read by bypassing SSTable merging and bloom filter checks.

Stored off-heap to avoid JVM garbage collection pressure, but can consume
significant system RAM. Only recommended for hot rows where a small fraction
of data receives the vast majority of reads (e.g., trending items).

Disabled by default.

## Chunk cache (off-heap)

SSTables are stored on disk as compressed blocks (chunks). The chunk cache
holds the uncompressed versions of recently accessed blocks in memory. If
another query needs data from the same block, Cassandra skips the CPU cost
of decompression.

Enabled by default.

## Counter cache (on-heap)

Specialized for the counter data type. Updating a counter requires a
read-before-write to get the current value, which causes lock contention
under heavy load. The counter cache holds current values of the most active
counters, avoiding disk reads for each increment or decrement.

Enabled by default.

## Cache warming

When a node restarts, its caches are empty and performance drops until they
warm up. Cassandra mitigates this by periodically saving cache key snapshots
to disk. On boot, the node reads these snapshots and pre-loads entries so it
returns to peak performance immediately after a maintenance window.

## Summary

| Cache         | Location      | Stores                          | Default  |
|---------------|---------------|---------------------------------|----------|
| Key cache     | On-heap (JVM) | Disk offsets for partition keys | Enabled  |
| Row cache     | Off-heap      | Full row data                   | Disabled |
| Chunk cache   | Off-heap      | Decompressed SSTable blocks     | Enabled  |
| Counter cache | On-heap (JVM) | Recent counter values           | Enabled  |

## Related

- [Bloom filters](bloom-filters.md) - Probabilistic layer checked before caches
- [Storage model](storage-model.md) - Write path and SSTable structure
- [Compaction](compaction.md) - Invalidates cached data when SSTables merge

---

Return to [Cassandra](_index.md)
