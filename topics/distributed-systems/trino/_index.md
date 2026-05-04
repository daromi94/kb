# Trino

Distributed SQL query engine for fast analytics over data that lives in many
heterogeneous sources, with no storage layer of its own.

## Notes

- [Overview](overview.md) - What Trino is and when it fits
- [Architecture](architecture.md) - Cluster components and topology
- [Connector API](connector-api.md) - Pluggable data sources
- [Query lifecycle](query-lifecycle.md) - From SQL to running tasks
- [Query optimization](query-optimization.md) - Cost-based plan rewriting
- [Execution model](execution-model.md) - In-memory pipelined processing
- [Runtime code generation](runtime-codegen.md) - Per-query JVM bytecode
- [Backpressure](backpressure.md) - Memory-bounded flow control
- [Coordinator deep dive](coordinator-deep-dive.md) - Internals in depth
- [Discovery service](discovery-service.md) - Worker liveness registry
- [Query tracker](query-tracker.md) - Per-coordinator query registry
- [Resource groups](resource-groups.md) - Cluster-wide admission control
- [Query termination](query-termination.md) - How queries end early
- [Fault-tolerant execution](fault-tolerant-execution.md) - Resilient batch mode
- [Architectural lessons](architectural-lessons.md) - Design principles

---

Return to [Distributed systems](../_index.md)
