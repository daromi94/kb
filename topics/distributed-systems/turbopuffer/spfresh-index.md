# SPFresh index

Turbopuffer uses SPFresh, a centroid-based vector index, instead of
the more common HNSW (Hierarchical Navigable Small World) graph
index. This choice is driven entirely by the realities of searching
over object storage.

## Why HNSW Fails on Object Storage

HNSW navigates a graph by following edges from node to node. Each hop
is a small random read. On local NVMe this is fast, but on S3 each
hop becomes a high-latency network roundtrip. A typical HNSW search
requires dozens of hops, making the cumulative latency unacceptable.

## Centroid-Based Search

SPFresh organizes vectors into clusters, each represented by a
centroid. Search proceeds in two phases:

```
+---------------------------+
|  Query Vector             |
|         |                 |
|         | compare against |
|         v                 |
|  Centroid Index (small)   |
|         |                 |
|         | identify top    |
|         | clusters        |
|         v                 |
|  Fetch clusters (3-4      |
|  massive S3 reads)        |
|         |                 |
|         | scan vectors    |
|         v                 |
|  Return top-k results     |
+---------------------------+
```

1. **Coarse navigation.** Download a compact centroid index and find
   which clusters are nearest to the query vector.
2. **Bulk fetch.** Retrieve entire clusters in 3-4 large sequential
   reads from S3.

This aligns with object storage characteristics: high per-request
latency but massive throughput for large objects. A few big reads
vastly outperform many small random reads.

## Recall

SPFresh maintains 90-95% recall, even under complex metadata filters.
The system is tuned for high accuracy out of the box rather than
exposing index tuning parameters that users might misconfigure.

## Search Modes

Turbopuffer supports three search modes built on this foundation:

| Mode   | Engine  | Mechanism                                          |
|--------|---------|----------------------------------------------------|
| ANN    | SPFresh | Approximate nearest neighbor via centroid clusters |
| FTS    | BM25    | Keyword ranking by term frequency and uniqueness   |
| Hybrid | Both    | Multiple queries merged in one API call            |

Hybrid search combines semantic similarity (vector) with exact keyword
matching (BM25), allowing retrieval that captures both meaning and
specific terms.

## Related

- [Architecture](architecture.md) - Storage hierarchy that SPFresh is designed for
- [Tradeoffs](tradeoffs.md) - First-stage retrieval philosophy

---

Return to [Turbopuffer](_index.md)
