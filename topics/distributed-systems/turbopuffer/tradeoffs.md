# Tradeoffs

Turbopuffer's architecture makes deliberate engineering tradeoffs to
optimize for cost and scale over instantaneous writes and built-in
complexity.

## Write Latency vs. Throughput

Every write must be durably committed to S3 before acknowledgment,
creating a ~285ms write latency floor. In return, the append-only WAL
design delivers massive aggregate throughput (10,000+ vectors/sec per
namespace) without the rebalancing complexity of stateful clusters.

## Cold Start vs. Storage Cost

The first query to an inactive namespace takes ~400ms because data
must be fetched from S3. Subsequent queries hit the NVMe cache at
~8ms. Only actively queried namespaces consume NVMe/RAM resources;
inactive data remains in object storage.

Applications mitigate cold starts with pre-warming: issuing a
preflight query to hydrate the cache before the user begins searching.

## First-Stage Retrieval Focus

Turbopuffer is specialized for candidate generation, not end-to-end
ranking. It scans billions of vectors and narrows results to the top
100-1000 candidates. Final ranking happens in application code.

This is a deliberate scope limitation. The system avoids a complex
query DSL for deep ranking. Applications are expected to perform
second-stage reranking externally.

## Precision over Configuration

The system exposes few tuning knobs. Index parameters are managed
internally rather than requiring users to configure HNSW settings or
recall targets. This maintains high recall (>90%) even under complex
metadata filters, at the cost of less control for advanced users.

## Related

- [Architecture](architecture.md) - Core stateless compute model
- [SPFresh Index](spfresh-index.md) - Index design aligned with these tradeoffs
- [Consistency and Durability](consistency-and-durability.md) - Durability cost of the write path

---

Return to [Turbopuffer](_index.md)
