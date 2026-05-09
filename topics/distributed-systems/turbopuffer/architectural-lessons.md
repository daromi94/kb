# Architectural lessons

Turbopuffer reflects a post-cloud mindset: object storage is the
primary driver of durability and state, not a backup target bolted
onto a server-heavy cluster.

## Storage as primary disk

Traditional databases treat S3 as a backup destination. Turbopuffer
treats it as the primary disk. If the storage layer is durably
consistent, you can eliminate the complexity of a separate consensus
plane (ZooKeeper, Raft). There is no data rebalancing, no split-brain
risk, and near-zero operational overhead from coordination protocols.

## Elastic hydration

The system inflates and deflates resource usage based on actual query
traffic. Multi-tenancy is most efficient when you only pay for compute
on active data. The vast majority of data sits cold in object storage
and is hydrated to NVMe/RAM only during queries.

## Round-trip sensitivity dictates algorithm choice

HNSW is the industry standard for vector search, but its graph
traversal requires many small pointer-chasing hops — a disaster on
high-latency object storage. SPFresh replaces dozens of small random
reads with 3-4 massive sequential fetches. The general principle:
never use a pointer-heavy data structure on a high-latency network.
Match the access pattern to the storage medium.

## Separate compute from compute

Most systems separate compute from storage. Turbopuffer goes further
by separating query compute from indexing compute. Background tasks
like index building and compaction are CPU-heavy and spiky. Running
them on the same nodes as queries causes latency jitter (noisy
neighbor problem). Isolating them ensures a 10-million-vector write
batch does not affect search latency on other nodes.

## First-stage specialization

Rather than covering retrieval and ranking end-to-end, the
architecture focuses on high-recall candidate generation. It narrows
billions of items to ~1,000 candidates and delegates final reranking
to application code, keeping the database's scope narrow.

## Locality in stateless systems

Even when any node can serve any request, locality still matters.
Sticky routing sends queries for the same namespace to the same node,
maximizing NVMe cache hit rates and turning 400ms cold queries into
8ms warm ones — without sacrificing the ability to fail over instantly
to any other node.

---

Return to [Turbopuffer](_index.md)
