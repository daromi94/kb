# Commit Log

The commit log is the database's crash recovery mechanism—an append-only file
on disk that ensures data survives even if power is cut instantly.

## Why It Exists

Databases face a speed vs. safety dilemma:

- **RAM writes** are fast (nanoseconds) but volatile—power loss means data loss
- **Data file writes** (SSTables) are slow—they require sorting and organizing

The commit log bridges this gap. When you send a write:

1. Append data to the **commit log** on disk (fast, safe)
2. Write data to the **memtable** in RAM (fast, sortable)
3. Return success

If power fails, RAM data is lost. On restart, the node replays the commit log
to restore the memtable.

## Append-Only Design

The commit log only adds new records to the end—never editing or deleting in
the middle. This makes writes fast because the disk head doesn't jump around
(sequential I/O). Once written, entries are immutable.

## Write Path

```
       +----------------+
       |  Client Write  |
       +-------+--------+
               |
               v
       +-------+--------+
       |  ScyllaDB Node |
       +---+--------+---+
           |        |
           v        v
   +-------+---+ +--+--------+
   | Commit Log | |  Memtable |
   |   (Disk)   | |   (RAM)   |
   +-----+-----+ +-----+-----+
         |             |
         +------+------+
                |
                v
          +-----+-----+
          |    Ack    |
          +-----------+
```

## ScyllaDB Adaptations

In traditional databases like Cassandra, all threads fight for a lock to write
to the commit log. ScyllaDB adapts this for shard-per-core:

**No global locks.** Each shard manages its own write path, avoiding a single
contention point.

**Segment recycling.** Creating new files is slow. ScyllaDB recycles old commit
log segments—renaming empty files and overwriting them rather than deleting and
creating. This keeps latency predictable without spikes from OS file
allocation.

## Lifecycle

The commit log is a temporary buffer:

1. Data accumulates in the memtable (RAM)
2. When the memtable fills, it flushes to a permanent SSTable on disk
3. Once data is safely in the SSTable, corresponding commit log entries are
   truncated or recycled

| Aspect      | Description                                       |
| ----------- | ------------------------------------------------- |
| Purpose     | Durability and crash recovery                     |
| Speed       | Fast—sequential append-only I/O                   |
| Persistence | Temporary—deleted once flushed to SSTables        |
| ScyllaDB    | Recycled segments avoid file allocation overhead  |
