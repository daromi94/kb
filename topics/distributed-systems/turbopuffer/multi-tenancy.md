# Multi-tenancy

Multi-tenancy is implemented through namespace isolation and resource
sharing across stateless compute nodes.

## Namespaces

A namespace is an isolated logical container with its own prefix in
object storage. Each namespace maintains independent WAL entries,
indexes, and schema.

Best practice is one namespace per tenant (e.g., per user or per
application context). This natural partitioning means the system only
hydrates the data needed for a specific query, rather than scanning a
single massive global index.

## Documents and schema

Each document has a unique primary key (ID) that can be `u64`,
`UUID`, or string. Using native types like `u64` or `UUID` instead
of strings reduces storage footprint and improves scan speed.

Turbopuffer infers types from data or accepts a defined schema. All
vectors within a namespace must share the same dimensions, and
attribute types must be consistent across documents.

## Bin-packing

Each `./tpuf` binary serves multiple tenants. Small namespaces share
compute resources on the same node. Resource consumption scales with
active query volume, not the number of tenants.

## Sticky routing

The load balancer routes requests for a specific namespace to the
same query node when possible. This keeps the NVMe cache warm for
that namespace, avoiding repeated S3 fetches. If the preferred node
is unavailable, any other node can serve the request by pulling data
from object storage.

## Pre-warming

Applications can issue a preflight query to hydrate the cache before
the user starts searching. This hides cold-start latency by
triggering the S3-to-NVMe transfer while the user is still
navigating to the search interface.

## Related

- [Architecture](architecture.md) - Stateless compute and hydration model
- [Tradeoffs](tradeoffs.md) - Cold start implications of the caching model

---

Return to [Turbopuffer](_index.md)
