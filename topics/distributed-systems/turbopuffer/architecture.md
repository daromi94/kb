# Architecture

Turbopuffer is built on a stateless-compute, stateful-storage model
that decouples query processing from data persistence. Object storage
(S3/GCS) serves as the sole source of truth while NVMe SSDs and RAM
act as an ephemeral cache layer. The name "pufferfish" reflects this
design: the cache inflates on demand to serve active queries, then
deflates when data goes cold.

## Storage Hierarchy

The system manages three tiers of data access to balance cost and
performance:

```text
+--------------------------+
|       RAM (hottest)      |  ~8ms queries
+--------------------------+
|     NVMe SSD (warm)      |  Local to query nodes
+--------------------------+
|  Object Storage (S3/GCS) |  Source of truth, ~400ms cold reads
+--------------------------+
```

**Object storage** holds the WAL (`/wal`) and optimized index files
(`/index`). Data is pulled into the NVMe tier only when a namespace
is actively queried, and the hottest namespaces are promoted to RAM.
Inactive data remains in S3.

| Query State | Storage Layer  | Latency (p50) | Scenario                 |
|-------------|----------------|---------------|--------------------------|
| Cold        | Object Storage | ~400ms        | First query, rare access |
| Warm        | NVMe SSD / RAM | ~8ms          | Active search traffic    |

## Stateless Compute

Query nodes are stateless binaries. Because all persistent state
lives in object storage, nodes are interchangeable. A failed node is
replaced without data rebalancing or state synchronization. New nodes
pull the required data from S3 on demand.

## Compute-Compute Separation

The system splits processing into two specialized node types:

- **Query nodes** handle API requests, searches, and cache management.
  Optimized for low-latency response.
- **Indexing nodes** run in the background, consuming WAL entries and
  building optimized SPFresh and BM25 indexes.

Both types auto-scale independently. A massive data import on indexing
nodes does not affect query latency for other tenants.

## Hydration Model

The system uses pull-on-demand caching:

- Only actively searched namespaces occupy NVMe/RAM resources.
- Evicted data falls back to S3.
- Applications can pre-warm the cache by issuing a preflight query
  before the user begins searching.

Resource consumption scales with active query traffic, not total
dataset size.

## Durability via Object Storage Replication

Traditional vector databases replicate data across multiple local SSDs
or EBS volumes for durability. Turbopuffer delegates replication to
object storage, eliminating the need for application-level replication
across disk-heavy servers. The tradeoff is higher per-write latency
from the S3 roundtrip.

## Related

- [SPFresh index](spfresh-index.md) - Search index designed for object storage access patterns
- [Consistency and durability](consistency-and-durability.md) - WAL design and consistency model
- [Multi-Tenancy](multi-tenancy.md) - Namespace isolation and resource sharing
- [Tradeoffs](tradeoffs.md) - Deliberate design tradeoffs and fit assessment

---

Return to [Turbopuffer](_index.md)
