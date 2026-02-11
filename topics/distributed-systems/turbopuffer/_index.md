# Turbopuffer

Vector database built on stateless compute with object storage as
the sole source of truth. Designed for cost-effective multi-tenant
vector search at trillion-document scale.

## Notes

- [Architecture](architecture.md) - Stateless compute, tiered caching, hydration model
- [SPFresh Index](spfresh-index.md) - Centroid-based index optimized for object storage
- [Consistency and Durability](consistency-and-durability.md) - WAL on S3, strong/eventual consistency, ACID
- [Multi-Tenancy](multi-tenancy.md) - Namespace isolation, bin-packing, sticky routing
- [Tradeoffs](tradeoffs.md) - Write latency, cold starts, first-stage retrieval focus
- [Architectural Lessons](architectural-lessons.md) - Transferable design principles
