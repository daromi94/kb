# Mechanical sympathy

Every design choice in the inverted index maps to a physical constraint
of RAM, CPU caches, OS paging, or disk throughput.

## Dictionary in RAM, postings on disk

RAM is fast but small. Disk is vast but slow. The index is split along
that seam: the term dictionary — aggressively compressed with Finite
State Transducers — stays memory-resident, while the heavy postings
lists live on disk. The in-memory dictionary stores a byte offset for
each term, so locating a postings list is a single direct access rather
than a search.

## Sorted IDs and delta encoding

Moving bytes from RAM to the CPU is itself a bottleneck. Sorted doc IDs
enable delta encoding, which compresses the gaps to a handful of bits:

- Absolute: `[1000000, 1000005, 1000012]` — 32 bits each
- Deltas:   `[1000000, 5, 7]` — anchor wide, gaps fit in a few bits each

Tight bit-packing shrinks the I/O payload and lets the CPU pull whole
blocks of postings into L1/L2 cache in a single fetch, where SIMD
instructions process them in parallel.

## Skip lists

Sequential I/O is fast, but reading millions of bytes you don't need is
still waste. Skip lists inject forward pointers at regular intervals
into the postings data. When intersecting a rare term with a very
common one, the engine leapfrogs over blocks that cannot contain a
match — bytes that are never read from disk at all.

## Immutable segments

Mutable files invalidate OS page caches and force locks on every
access. Segments, once written, are sealed. The consequences:

- **Lock-free reads.** Thousands of search threads share the same
  segment without coordination because the data cannot change under
  them.
- **Page cache alignment.** The OS memory-maps segment files directly
  into the page cache. Read-only pages never go dirty, so the kernel
  never tracks writes, invalidates caches, or flushes. Disk-backed data
  serves at near-RAM latency.

## Related

- [Inverted index](inverted-index.md) - Core data structure

---

Return to [Elasticsearch](_index.md)
