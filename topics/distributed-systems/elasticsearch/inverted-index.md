# Inverted index

An **inverted index** maps each term to the list of documents containing
it — the foundational data structure of text search. The natural on-disk
layout is a **forward index**: documents mapping to their terms. But
answering "which documents contain *fox*?" against a forward index
requires scanning every document. Inversion turns the query into a
dictionary lookup plus a read of a precomputed list.

## The two halves

**Term dictionary.** The set of all unique terms in the corpus. Small,
randomly accessed, kept resident in memory. Lucene uses Finite State
Transducers — DAGs that share both prefixes and suffixes — for
near-optimal compression.

**Postings lists.** For each term, a list of postings recording where the
term appears. Large, accessed sequentially, kept on disk.

## Anatomy of a posting

A posting records one occurrence of a term:

| Field     | Purpose                      |
|-----------|------------------------------|
| doc ID    | Boolean retrieval            |
| frequency | BM25 / TF-IDF scoring input  |
| positions | Phrase and proximity queries |
| offsets   | Character ranges, highlights |

Fields opt into the level of detail they need. Storing less means smaller
indexes and faster queries.

## The sorted invariant

Doc IDs within a postings list are strictly ascending. This unlocks two
key optimizations.

**Delta encoding.** Store gaps instead of absolute IDs: `[17, 42, 43]`
becomes `[17, 25, 1]`. Gaps are small integers and compress to one or two
bytes per posting with PFOR-delta over fixed blocks.

**Skip-based intersection.** To answer `cat AND dog`, walk both postings
lists with two cursors, advancing whichever is behind. Sparse forward
pointers let the cursor for *the* (millions of postings) leap ahead to
catch up with *fox* (a few hundred) without decoding everything in
between. Postings flow through scoring block by block; the engine never
holds a full list in memory.

## Immutability and segments

Inverted indexes are hostile to in-place updates — inserting into a
common term's postings list would shift gigabytes of compressed data. The
solution is **segment-based immutability**: new documents accumulate in
an in-memory buffer and are flushed as new immutable segments, each with
its own complete inverted index. Queries run across all segments and
merge results. Deletes are recorded as a bitmap of live doc IDs; a
background merge process rewrites small segments into larger ones and
drops deleted documents. Essentially an LSM-tree applied to inverted
indexes.

---

Return to [Elasticsearch](_index.md)
