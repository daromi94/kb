# Trino

Distributed SQL query engine for fast analytics over data that lives in many
heterogeneous sources, with no storage layer of its own.

## Notes

- [Overview](overview.md) - What Trino is and when it fits
- [Architecture](architecture.md) - Coordinator, workers, and connectors
- [Coordinator deep dive](coordinator-deep-dive.md) - Coordinator internals in depth
- [Discovery service](discovery-service.md) - Worker registry and liveness
- [Query tracker](query-tracker.md) - Per-coordinator query registry
- [Query termination](query-termination.md) - Failures, cancellations, deadlines
- [Connector API](connector-api.md) - How Trino plugs into data sources
- [Query lifecycle](query-lifecycle.md) - From SQL to running tasks
- [Query optimization](query-optimization.md) - Cost-based planning and pushdown
- [Execution model](execution-model.md) - In-memory pipelined processing
- [Runtime code generation](runtime-codegen.md) - Per-query JVM bytecode
- [Fault-tolerant execution](fault-tolerant-execution.md) - Spooled exchanges for batch

---

Return to [Distributed systems](../_index.md)
