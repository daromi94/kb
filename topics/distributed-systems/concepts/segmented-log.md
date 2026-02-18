# Segmented log

A single, ever-growing write-ahead log eventually exhausts disk space and
makes recovery slow. The segmented log pattern breaks the monolithic file
into a series of smaller files called **segments**, making cleanup,
recovery, and replication practical.

## How it works

Instead of one `wal.log` file, the system maintains a collection of files
named by their starting offset (e.g., `000001.log`, `000050.log`).

**Active segment.** Only one segment accepts writes at a time. New entries
are appended to it.

**Inactive segments.** When the active segment reaches a size or time
limit it is closed and becomes immutable. A new active segment is created.

**Log index.** An in-memory index maps keys or offsets to specific files
and positions so reads avoid scanning every segment.

## Benefits

**Efficient cleanup.** With a single file you cannot remove old data
without rewriting the whole thing. With segments the system deletes the
oldest file once its data has expired or been flushed to permanent
storage.

**Faster recovery.** After a crash the system only replays the most
recent segments. Older segments that have already been checkpointed are
skipped, reducing startup time.

**Simpler replication.** When a follower joins a cluster the leader ships
whole segment files rather than streaming individual entries from one
giant log.

## Cleanup strategies

**Deletion.** Drop the oldest segment files based on a time or size
retention policy.

**Compaction.** Scan inactive segments and keep only the latest value for
each key, then merge the remaining data into a new smaller segment and
delete the originals.

## On-disk layout

In systems like Kafka each segment consists of companion files:

- `.log` — the actual messages or data entries
- `.index` — a sparse index mapping offsets to byte positions in the
  `.log` file for fast lookups without a full scan
- `.timeindex` — a sparse index mapping timestamps to offsets for
  time-based lookups

The result is a log that behaves like an infinite stream while physically
consisting of finite, disposable files.

## Related

- [Write-ahead log](write-ahead-log.md) - The pattern that segmented
  logs build on
- [Low-water mark](low-water-mark.md) - Determines which segments are
  safe to delete
- [Bloom filters](bloom-filters.md) - Often used alongside segment
  indexes to skip segments that cannot contain a key

---

Return to [Concepts](_index.md)
