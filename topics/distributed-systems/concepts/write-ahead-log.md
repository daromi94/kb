# Write-ahead log

A Write-Ahead Log (WAL) provides **atomicity** and **durability** (the A and D
in ACID). The core premise: any change must be recorded in a stable log file
before being applied to actual data files.

If the system crashes, the database recovers by replaying the log to restore
data to its last consistent state.

## How the WAL process works

In a typical database operation (like `UPDATE` or `INSERT`), the system follows
a specific sequence:

1. **Transaction begins** - A user sends a command to modify data
2. **Log entry creation** - The database creates a record describing the change
   (e.g., "Change value in Row 5 from A to B")
3. **Flushing the log** - The log entry is written to the WAL file on disk; the
   system waits for the storage controller to confirm the write is durable
4. **Buffer cache update** - Once the log is safe on disk, the database updates
   the record in memory (the buffer cache); the data file on disk is *not*
   updated yet
5. **Commit** - The transaction is marked as successful to the user
6. **Checkpointing** - Periodically, the database flushes modified data from
   memory to the main data files and clears old log entries

## Why use a WAL

Using a WAL is more efficient than updating main data files immediately.

### Sequential vs random I/O

Updating a B-Tree or heap file involves random I/O — the disk head jumps to
different physical locations. A WAL is **append-only**, using sequential I/O.
Writing to the end of a file is vastly faster than updating pages scattered
across a disk. The system calls `fsync` to force the OS to flush the log
entry to stable storage before acknowledging the write.

### Immutability and segmentation

Log entries are never modified. If a value is updated, a new entry is
appended. To prevent unbounded growth, the WAL is split into segments.
Once a segment's data has been flushed to the main data files, the
segment can be deleted or archived.

### Recovery

If power is lost before the buffer cache flushes to data files:

- Data files are stale or inconsistent
- On restart, the database reads the WAL from the last checkpoint
- It replays committed transactions in order to restore consistent state

## WAL in distributed systems

In distributed databases like ScyllaDB or Cassandra, the WAL is called a
**CommitLog**. When a write request arrives, it writes to the CommitLog and the
in-memory Memtable simultaneously. Because the Memtable is volatile, the
CommitLog serves as the source of truth if a node reboots before the Memtable
flushes to an SSTable (the immutable on-disk storage).

| Feature     | Standard update (no WAL)          | WAL-based update                  |
|-------------|-----------------------------------|-----------------------------------|
| Disk access | Random I/O (slow)                 | Sequential I/O (fast)             |
| Integrity   | Risk of partial writes/corruption | High (log is the source of truth) |
| Performance | Latency tied to data file updates | Latency tied to simple appends    |

## Related

- [Segmented log](segmented-log.md) - Breaking the WAL into manageable
  file segments for cleanup and recovery
- [Commit log](../scylla-db/commit-log.md) - ScyllaDB's WAL implementation

---

Return to [Concepts](_index.md)
