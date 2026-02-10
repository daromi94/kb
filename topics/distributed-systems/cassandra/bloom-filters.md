# Bloom filters

In the Cassandra read path, bloom filters act as a high-speed gatekeeper
that prevents expensive disk I/O for data that does not exist in a specific
SSTable. Because the LSM-tree storage model spreads a partition across
multiple SSTable files, checking every file on every read would be
prohibitively slow. Bloom filters provide a nearly instantaneous "definitely
not" or "maybe."

## Mechanism

A bloom filter is a space-efficient probabilistic data structure using a bit
array of size $m$ and $k$ hash functions.

**Adding an element:** When a row is written to an SSTable, its partition key
is run through the $k$ hash functions. Each function produces a position in
the bit array, and those bits are set to 1.

**Querying an element:** The same hash functions are applied to the
requested key.

- If any bit at the computed positions is 0, the key definitely does not
  exist in that SSTable. Cassandra skips the file entirely.
- If all bits are 1, the key might exist. Cassandra proceeds to check the
  on-disk index to confirm.

## False positives

Bloom filters have no false negatives: a "no" answer is 100% accurate. They
can produce false positives when different keys happen to hash to the same
set of bit positions, causing a wasted disk seek when Cassandra checks the
SSTable and finds nothing.

## Tuning

The `bloom_filter_fp_chance` table property controls the false positive rate.
This is a direct trade-off between memory and disk I/O.

| FP chance | Memory usage              | Disk performance            | Fit                             |
|-----------|---------------------------|-----------------------------|---------------------------------|
| 0.01      | Higher (larger bit array) | Faster (fewer wasted seeks) | Read-heavy workloads            |
| 0.1       | Lower (smaller bit array) | Slower (more wasted seeks)  | Write-heavy or rarely-read data |

Bloom filters are stored in off-heap memory (outside the JVM heap), so they
do not contribute to garbage collection pressure but still consume physical
RAM.

## Position in the read path

When a read request arrives at a node:

1. Check the **row cache** (if enabled).
2. Check the **bloom filter** for each SSTable.
3. If the bloom filter says "maybe," check the **key cache**.
4. If not cached, check the **partition summary** and **partition index** on
   disk.
5. Read the **SSTable** data block.

## Related

- [Storage model](storage-model.md) - Write path and SSTable lifecycle
- [Caching](caching.md) - Key cache, row cache, and other layers
- [Compaction](compaction.md) - Rebuilds bloom filters for merged SSTables

---

Return to [Cassandra](_index.md)
