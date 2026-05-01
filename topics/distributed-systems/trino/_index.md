# Trino

Distributed SQL query engine for fast analytics over data that lives in many
heterogeneous sources, with no storage layer of its own.

## Notes

- [Overview](overview.md) - What Trino is and when it fits
- [Architecture](architecture.md) - Cluster components and topology
- [Connector API](connector-api.md) - Pluggable data sources
- [Coordinator deep dive](coordinator-deep-dive.md) - Coordinator internals in depth
- [Discovery service](discovery-service.md) - Worker liveness registry
- [Query tracker](query-tracker.md) - Per-coordinator query registry
- [Resource groups](resource-groups.md) - Cluster-wide admission control
- [Query termination](query-termination.md) - How queries end early
- [Query lifecycle](query-lifecycle.md) - From SQL to running tasks
- [Query optimization](query-optimization.md) - Cost-based plan rewriting
- [Execution model](execution-model.md) - In-memory pipelined processing
- [Runtime code generation](runtime-codegen.md) - Per-query JVM bytecode
- [Fault-tolerant execution](fault-tolerant-execution.md) - Resilient execution for batch

---

Return to [Distributed systems](../_index.md)
