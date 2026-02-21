# Turbopuffer

Vector database built on stateless compute with object storage as
the sole source of truth. Designed for cost-effective multi-tenant
vector search at trillion-document scale.

## Notes

- [Architecture](architecture.md) - Stateless compute, tiered caching, hydration model
- [SPFresh index](spfresh-index.md) - Centroid-based index optimized for object storage
- [Consistency and durability](consistency-and-durability.md) - WAL on S3, strong/eventual consistency, ACID
- [Multi-tenancy](multi-tenancy.md) - Namespace isolation, bin-packing, sticky routing
- [Building on object storage](building-on-object-storage.md) - First-principles database design walkthrough
- [Tradeoffs](tradeoffs.md) - Write latency, cold starts, first-stage retrieval focus
- [Architectural lessons](architectural-lessons.md) - Transferable design principles

---

Return to [Distributed systems](../_index.md)
