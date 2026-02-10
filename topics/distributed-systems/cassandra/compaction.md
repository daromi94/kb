# Compaction

Compaction is the background maintenance process that makes Cassandra's
append-only storage model sustainable. Because SSTables are immutable, every
update or delete creates a new data fragment on disk. Without compaction,
reads would eventually scan hundreds of files to reconstruct a single row.

## Merge and purge

Compaction is effectively a merge sort over multiple SSTables, producing one
optimized SSTable as output.

**Merging:** Combines fragments of the same partition from different files.

**Resolution:** If the same cell exists in multiple files, only the version
with the highest (newest) timestamp is kept.

**Eviction:** This is the only time Cassandra physically removes deleted
data. If a tombstone is older than `gc_grace_seconds`, both the marker and
the shadowed data are permanently dropped.

**Re-indexing:** A fresh bloom filter, partition summary, and partition index
are created for the new file.

## Why compaction matters

Compaction balances the trade-off between write speed and read performance.

**Reducing disk seeks:** Instead of hitting five SSTables to reconstruct a
row, the reader hits one.

**Reclaiming space:** Old updates and expired tombstones are pruned away.

**I/O amortization:** Background work keeps the write path a simple,
instant append to the commit log.

## Compaction strategies

| Strategy          | Logic                                          | Best for                                            |
|-------------------|------------------------------------------------|-----------------------------------------------------|
| SizeTiered (STCS) | Merges SSTables of similar sizes               | Write-heavy workloads                               |
| Leveled (LCS)     | Organizes data into levels of fixed-size files | Read-heavy workloads (90% of reads hit one SSTable) |
| TimeWindow (TWCS) | Groups data into time-based buckets            | Time-series data (logs, IoT)                        |

**STCS:** Efficient for ingest but can accumulate many SSTables for a single
partition, increasing read amplification.

**LCS:** Guarantees bounded read amplification at the cost of higher write
amplification from more frequent compactions.

**TWCS:** Aligns with TTL-based data. Entire SSTable files can be dropped
once every row in the time window expires.

## Anticompaction

A specialized split operation that supports incremental repair. After a
repair run, anticompaction takes an existing SSTable and splits it into two
files: one containing verified (repaired) data and one containing unverified
data. This prevents the repair process from re-hashing already-verified
ranges.

## Compaction debt

Compaction consumes disk I/O and CPU because it reads and writes files
simultaneously.

**Temporary space spike:** Both old and new SSTables exist on disk until the
merge completes and the old files are deleted.

**Falling behind:** If the write rate exceeds the compaction throughput, the
cluster accumulates compaction debt: a growing backlog of small SSTables
that degrades read performance.

## Related

- [Storage model](storage-model.md) - Write path and SSTable lifecycle
- [Tombstones](tombstones.md) - Deletion markers purged during compaction
- [Bloom filters](bloom-filters.md) - Rebuilt for each new SSTable
- [LSM-tree](lsm-tree.md) - Architectural foundation for compaction

---

Return to [Cassandra](_index.md)
