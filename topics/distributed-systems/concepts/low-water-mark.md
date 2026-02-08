# Low-Water Mark

The low-water mark is the log index (or timestamp) before which all
entries are guaranteed to be safely processed and stored elsewhere,
making them safe to delete. It solves the cleanup problem for segmented
logs: old segments must not be removed while any component still depends
on them.

## What holds the mark back

The low-water mark is the **minimum** of several competing constraints:

**Snapshot/checkpoint.** If the system takes a state snapshot at index
500, log entries before 500 are redundant for recovery purposes.

**Replication progress.** With three followers, if the slowest has only
processed up to index 450, the leader cannot advance the mark past 450
without orphaning that follower.

**Retention policy.** A time-based rule (e.g., "keep data for 7 days")
may set the absolute lower bound regardless of the other factors.

## Log truncation

Once the mark advances, the system performs log truncation in the
background:

1. Identify all segments whose highest index falls below the mark
2. Delete those segment files from disk
3. Continue writing to the active segment without interruption

## High-water mark vs low-water mark

These two markers define the lifecycle of a log entry: the high-water
mark governs what clients can read; the low-water mark governs what the
system can discard.

| Feature  | High-water mark                              | Low-water mark                               |
|----------|----------------------------------------------|----------------------------------------------|
| Location | The front of the log                         | The tail of the log                          |
| Purpose  | Defines what is **safe to read** (committed) | Defines what is **safe to delete** (cleaned) |
| Consumer | Clients waiting for data                     | The system / garbage collector               |
| Movement | Moves forward as replicas acknowledge writes | Moves forward as snapshots complete          |

## The slow-follower problem

If the low-water mark advances too quickly, a follower that was offline
for an extended period may find the log entries it needs have already
been deleted. In this case the follower cannot catch up incrementally
and must instead undergo a **state transfer** where the leader sends a
full snapshot of the current state rather than replaying log entries.

## Related

- [Segmented log](segmented-log.md) - The log structure that the
  low-water mark cleans up
- [Replication](replication.md) - Follower progress is a key input to
  the low-water mark

---

Return to [Concepts](_index.md)
