# Tombstones

In a distributed system, deleting data is more complex than simply erasing
bytes. If a node misses a deletion and later syncs with its peers, it could
resurrect the dead data, believing the other nodes are the ones missing a
record. Cassandra solves this with tombstones — special markers that record
deletions as writes.

## How tombstones work

When a `DELETE` is issued, Cassandra does not erase data on disk. It writes
a tombstone to the current memtable, which is later flushed to an SSTable
like any other write.

**Contents:** A tombstone includes the timestamp of the deletion and the
primary key of the data being deleted.

**Shadowing:** During a read, Cassandra merges data from multiple SSTables.
If it finds both a record and a tombstone for the same key, it compares
timestamps. If the tombstone is newer, the record is shadowed and not
returned to the client.

## Preventing data resurrection

Without tombstones, a node that was offline during a deletion would still
hold the old data. When it performs an anti-entropy repair with its peers,
it would see that they "lack" the data and helpfully copy its stale version
back. Tombstones prevent this by making the deletion a tangible piece of
data that propagates through gossip and repair just like a normal write.

## gc_grace_seconds

Tombstones cannot remain forever — they consume disk space and slow reads.
They are removed during compaction, but only after the `gc_grace_seconds`
period has elapsed.

**Default:** 10 days (864000 seconds).

**Logic:** This window gives an offline node time to return and learn about
the deletion via repair before the tombstone is discarded.

**Risk:** If a node stays offline longer than `gc_grace_seconds`, its peers
may have already compacted the tombstone away. When that node returns, it
resurrects the data because the tombstone marker no longer exists.

## Performance impact

Tombstones are a common source of read latency degradation, often called
tombstone pressure.

**Read overhead:** A query may have to scan through thousands of tombstones
before finding a live row, especially when individual rows or columns are
deleted frequently.

**Partition-level deletes:** Deleting an entire partition is significantly
more efficient than deleting individual rows. A single partition tombstone
lets Cassandra skip an entire SSTable section.

## Deletion lifecycle

| Phase        | Action                                  | Purpose                                      |
|--------------|-----------------------------------------|----------------------------------------------|
| Execution    | `DELETE` issued                         | Triggers a write, not an erase               |
| Storage      | Tombstone written to memtable / SSTable | Marks the data as dead with a timestamp      |
| Grace period | Waits for `gc_grace_seconds`            | Allows offline nodes time to sync the delete |
| Compaction   | Tombstone and shadowed data merged      | Physically removes data from disk            |
| Eviction     | Data is gone permanently                | Reclaims disk space and improves read speed  |

## Related

- [Compaction](compaction.md) - When tombstones are physically purged
- [Anti-entropy](anti-entropy.md) - Repair that propagates deletions
- [Storage model](storage-model.md) - SSTable immutability and the write path
- [Data modeling tips](data-modeling-tips.md) - Avoiding tombstone buildup

---

Return to [Cassandra](_index.md)
