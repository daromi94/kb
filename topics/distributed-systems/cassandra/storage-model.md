# Storage model

In Cassandra, the storage model is based on an LSM-tree (Log-Structured
Merge-Tree) architecture. This design is specifically optimized for high write
throughput by ensuring that almost all write operations are sequential rather
than random.

Cassandra's storage engine operates through a specific path that moves data from
memory to immutable disk files.

## The write path

When a write request is received by a node, it follows a strict sequence to
ensure both speed and durability:

1. **Commit log:** The write is first appended to a commit log on disk. This is
   a simple, append-only file used for crash recovery. If the node loses power,
   it replays this log to recover data that wasn't yet saved to permanent files.

2. **Memtable:** Simultaneously, the data is written to an in-memory structure
   called a memtable. This is a sorted buffer (often organized as a trie or
   skip-list) that holds the data in its logical order.

3. **Acknowledgment:** Once the data is in the commit log and the memtable, the
   node sends an acknowledgment back to the coordinator/client. This is why
   writes are so fast; there is no waiting for complex disk seeks.

## SSTables (sorted string tables)

When a memtable reaches a certain size threshold (or when the node is shut
down), it is flushed to disk as an SSTable.

**Immutability:** SSTables are immutable. Once written, they are never modified.
If you update or delete a row, Cassandra simply writes the new version to a new
SSTable.

**Sequential I/O:** Flushes are sequential writes, which are much faster than
the random-access updates used by traditional B-tree databases.

**Multiple files:** Because SSTables are immutable, a single row might have
fragments spread across multiple SSTable files on disk (the original insert in
one, an update in another, a delete in a third).

## Deletes and tombstones

Because SSTables cannot be changed, Cassandra cannot simply erase a row from an
existing file. Instead, it performs a tombstone write.

A tombstone is a special marker with a timestamp indicating that a specific
piece of data is deleted. During a read, Cassandra merges all relevant SSTables
and uses the tombstone to hide older versions of the data.

## Compaction

To prevent infinite accumulation of SSTables and to reclaim space from deleted
data, Cassandra performs compaction in the background.

**Merging:** The system takes multiple SSTables and merges them into one new,
larger SSTable.

**Resolution:** During the merge, Cassandra compares timestamps for the same
cell and only keeps the newest version.

**Eviction:** If a tombstone is older than a certain threshold (`gc_grace_seconds`),
the tombstone and the data it shadows are finally dropped from disk entirely.

## Read path optimization

Since data is spread across multiple immutable files, Cassandra uses several
helper structures to avoid scanning every file on disk:

**Bloom filters:** A probabilistic structure that can quickly tell Cassandra if
a specific partition key definitely does not exist in an SSTable.

**Partition index/summary:** Helps locate the exact offset of a partition within
the large SSTable file.

**Key cache:** Stores the location of frequently accessed keys in memory to skip
disk index lookups.

## Component summary

| Component        | Location | Role                               |
|------------------|----------|------------------------------------|
| **Commit log**   | Disk     | Durability and crash recovery      |
| **Memtable**     | RAM      | Fast buffer and recent data read   |
| **SSTable**      | Disk     | Persistent, immutable storage      |
| **Bloom filter** | RAM/Disk | Read optimization (skipping files) |

## Related

- [Data model](data-model.md) - Logical data structure
- [LSM-tree](lsm-tree.md) - Architectural foundation for the storage engine
- [Bloom filters](bloom-filters.md) - Probabilistic read path optimization
- [Caching](caching.md) - Key, row, chunk, and counter caches
- [Compaction](compaction.md) - SSTable merge strategies in depth
- [Tombstones](tombstones.md) - Deletion markers and gc_grace_seconds
- [Fault tolerance](fault-tolerance.md) - How the commit log aids recovery
- [Data modeling tips](data-modeling-tips.md) - Avoiding tombstone buildup

---

Return to [Cassandra](_index.md)
