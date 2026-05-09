# Building on object storage

A first-principles walkthrough of building a database on object
storage, illustrating each design decision as a response to a
concrete scaling problem.

## WAL as the database

The simplest possible database on object storage is a write-ahead
log. Each write creates an immutable file in a `/wal` prefix:

```text
/wal/1.bin
/wal/2.bin
/wal/3.bin
```

Each entry records a type (insert, delete) and the payload. A query
performs a full scan of all WAL entries, respecting inserts and
deletes. This is a real database: it supports any query, has full
time-travel capability, and never loses data. It just scales
terribly.

## Adding a cache layer

WAL entries are immutable, so they cache perfectly. Add an in-memory
cache, then an NVMe SSD cache tier. Queries check caches before
fetching from object storage. Performance improves dramatically for
warm data.

## Derived indexes

Full scans are slow. Build in-memory derived indexes over the WAL:

| Query Type   | Index Structure |
|--------------|-----------------|
| Point lookup | Hash map        |
| Range scan   | B-tree          |

The index is rebuilt from the WAL on startup. For strong consistency,
issue a `LIST` call to object storage before each query to discover
new WAL entries, then update the index from any cached entries.

## Persisting indexes

In-memory indexes are lost when nodes restart. Serialize the index
to object storage alongside a pointer to the WAL entry it covers:

```text
/btree.bin  (covers through /wal/42.bin)
```

On cold start, download the persisted index and replay only WAL
entries after entry 42. This drastically reduces recovery time
compared to replaying the entire log.

## Reducing round trips

Walking a B-tree stored in object storage requires one round trip
per tree level. At ~250ms per S3 GET (p90), a tree of depth 20
takes 5 seconds. The fix: widen each node to reduce depth. Use fat
B+-tree nodes so the tree has only 3-4 levels, bringing cold point
lookups down to hundreds of milliseconds. Cache upper layers for
frequently accessed data.

## Evolution toward LSM

Rewriting the entire index to object storage on every update creates
enormous write amplification. Instead, flush sorted batches of index
updates as separate files and merge results at query time. This is
the core LSM idea: append sorted runs, compact them periodically.
Compaction merges small files into larger ones, reducing read
amplification at the cost of background I/O.

## Conflict resolution for multiple writers

| Strategy           | Mechanism                                | Ordering    |
|--------------------|------------------------------------------|-------------|
| Single writer      | One node holds exclusive write authority | Strict      |
| External lock      | ZooKeeper/etcd grants write lease        | Strict      |
| Conditional writes | Put-if-not-exists on object storage      | Strict      |
| UUID v7 filenames  | Time-ordered UUIDs eliminate conflicts   | Approximate |

Conditional writes use object storage's native compare-and-swap:
attempt to write `/wal/4.bin` with a condition that the key does
not exist. If another writer already created it, the write is
rejected and the client retries with a higher sequence number.

## Group commits and batching

Individual writes to object storage are expensive (~100-250ms each).
Group commit coalesces writes arriving within a time window into a
single WAL entry, then acknowledges all clients at once. This is
analogous to MySQL's group commit: a single `fsync` (~1ms on SSD)
can durably commit 40 transactions instead of one.

On object storage the same principle applies at a different
timescale. A 250ms batch window reduces put amplification to four
puts per second while keeping write latency acceptable for search
workloads.

**Time-based vs size-based flushing.** Time-based batching (flush
every N ms) is simpler. Size-based batching (flush at N bytes) caps
network utilization. A blanket answer does not exist; production
systems use a hybrid tuned to real workload characteristics.

## Serialization formats

| Format    | Deserialization Speed | Random Access | Readability |
|-----------|-----------------------|---------------|-------------|
| JSON      | ~100s MB/s            | No            | High        |
| Protobuf  | Faster                | Limited       | Low         |
| Parquet   | Columnar-fast         | No            | Low         |
| Zero-copy | Instant (mmap)        | Yes           | None        |

Turbopuffer uses `rkyv`, a Rust zero-copy deserialization library.
Downloaded data is memory-mapped directly without parsing, which
eliminates CPU overhead when loading gigabytes of index data. They
chose a custom format over Arrow/Parquet for full control over on-
disk layout and round-trip minimization.

## Workload separation

| Workload    | Resource Profile           | Separation Rationale           |
|-------------|----------------------------|--------------------------------|
| Writes      | Network-bound, data proxy  | Co-locate with reads for cache |
| Reads       | Memory + latency-sensitive | Highest priority               |
| Compaction  | CPU + network-heavy        | Isolate to avoid query jitter  |
| Maintenance | Periodic (billing, GC)     | Run on compaction nodes        |

Writes and reads benefit from co-location: a write that lands on a
query node immediately populates the local cache, eliminating a
subsequent object storage fetch. Compaction is the strongest
candidate for separation due to its resource spikes. For vector
databases, index building dwarfs traditional compaction in compute
cost.

---

Return to [Turbopuffer](_index.md)
