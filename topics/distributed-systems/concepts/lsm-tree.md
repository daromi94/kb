# LSM tree

The Log-Structured Merge tree (LSM tree) is a storage engine
optimized for high write throughput. Writes go into an in-memory
buffer and periodically flush to immutable on-disk files, converting
random writes into sequential appends. The trade-off is a more
expensive read path: a key's most recent value may live in memory or
across multiple on-disk files.

## Components

The architecture separates a volatile in-memory tier from a
non-volatile on-disk tier:

- **Write-ahead log (WAL).** Every write appends to the WAL before
  acknowledgement; crash recovery replays it to rebuild the MemTable.
- **MemTable.** An in-memory sorted structure (typically a SkipList
  or Red-Black tree) that absorbs incoming writes and keeps them
  ordered by key.
- **SSTables (Sorted String Tables).** Immutable, key-ordered files
  on disk. When a MemTable reaches its size threshold it freezes and
  flushes to disk as an SSTable.

## Write path

1. Append the operation to the WAL.
2. Insert it into the MemTable.
3. Acknowledge the client.
4. When the MemTable fills, freeze it and flush it to disk as an
   SSTable. A fresh MemTable absorbs new writes.

Writes never mutate prior records in place, so all I/O is
sequential — the WAL is appended, the MemTable is updated in RAM,
and SSTables are written as whole files.

## Read path

A key's most recent value may live in the MemTable or any SSTable.
The read path checks them in reverse chronological order:

1. Check the MemTable.
2. If not found, check on-disk SSTables from newest to oldest.

To avoid scanning every SSTable, each file carries an associated
Bloom filter that answers "could this file contain this key?". A
negative response skips the file's disk read entirely.

## Tombstones

Deletes do not modify prior data. The engine writes a **tombstone** —
a marker entry that shadows older values for that key, so reads
return "not found". Tombstones propagate downward through compaction
and are dropped only when no older versions of the key remain
anywhere in the tree.

## Compaction

As MemTables flush, the number of SSTables grows. Reads degrade
(read amplification) and obsolete versions consume disk (space
amplification). Compaction is the background process that resolves
both.

Compaction merges multiple SSTables from one level into a single
SSTable at the next level. During the merge the engine sorts keys,
discards superseded versions, and drops tombstones whose targets
have no older copies remaining. The result is fewer, larger files at
deeper levels.

## Hot/cold separation

Because writes are append-only and compaction cascades downward,
data location correlates directly with data age. The structure
yields an emergent hot/cold separation — no separate caching logic
is required.

| Tier | Layers                | Hardware           | Contents                            |
|------|-----------------------|--------------------|-------------------------------------|
| Hot  | MemTable, L0 SSTables | RAM, fastest NVMe  | Recent writes; likely to be re-read |
| Warm | L1–L2 SSTables        | Local NVMe or SSD  | Slightly older; still local         |
| Cold | L3+ SSTables          | Cheap, dense media | Historical; large, rarely accessed  |

The layering maps naturally onto the hardware memory hierarchy.
Because the deepest levels are immutable and account for most of the
total volume, they can also be tiered to remote object storage,
keeping the local node's working set small.

---

Return to [Concepts](_index.md)
