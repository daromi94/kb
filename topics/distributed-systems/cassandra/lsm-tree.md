# LSM-tree

The log-structured merge-tree (LSM-tree) is the storage architecture at the
heart of Cassandra. It replaces the update-in-place model of traditional
B-tree databases with an append-only model that prioritizes write speed and
storage durability.

## B-tree vs LSM-tree

**B-tree (update-in-place):** When a row is updated, the database finds the
specific page on disk and overwrites it. This requires random I/O — seeking
to different physical locations — which is slow.

**LSM-tree (append-only):** New data is appended to the end of a log.
This uses sequential I/O, which is significantly faster on both spinning
disks and SSDs.

## Multi-stage data flow

Data flows through four stages from volatile memory to permanent storage:

1. **Write-ahead log (commit log):** Data is appended to a log on disk for
   crash recovery.
2. **Memtable (in-memory):** Data is simultaneously written to a sorted
   buffer in RAM for fast retrieval of recent writes.
3. **SSTables (on-disk):** When the memtable fills, it is flushed to disk
   as a sorted string table. Because the memtable is already sorted, the
   resulting file is perfectly ordered.
4. **Compaction:** Background merges combine multiple sorted files into
   larger ones, discarding old versions and reclaiming space.

## The read penalty

The trade-off for fast writes is that reads become more complex. In a
B-tree, a row has a single known location. In an LSM-tree, a row may have
fragments in the memtable and across several SSTables.

Two optimizations mitigate this:

**Bloom filters:** A probabilistic check that skips SSTables which
definitely do not contain the requested key.

**SSTable indexes:** Each SSTable has an internal index for jumping directly
to the correct position once the bloom filter returns "maybe."

## Comparison

| Aspect             | LSM-tree                                   | B-tree                                 |
|--------------------|--------------------------------------------|----------------------------------------|
| Write performance  | High (sequential appends)                  | Moderate (random seeks and updates)    |
| Storage efficiency | High (compressed, immutable blocks)        | Lower (requires free space for growth) |
| Concurrency        | High (no row-level write locks needed)     | Moderate (locks and latches)           |
| Read performance   | Variable (requires merging multiple files) | Stable (direct index lookup)           |

## Notable implementations

The LSM-tree pattern is used across the industry for high-throughput
storage:

- **Cassandra** — distributed NoSQL database
- **RocksDB / LevelDB** — embedded storage engines
- **HBase** — Hadoop-based NoSQL database
- **Bigtable** — Google's managed NoSQL service that inspired Cassandra

---

Return to [Cassandra](_index.md)
