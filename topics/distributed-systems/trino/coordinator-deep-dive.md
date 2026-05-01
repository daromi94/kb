# Coordinator deep dive

The coordinator turns a SQL string into a distributed execution graph and
orchestrates its run on workers. Internally it is a pipeline of translation
layers feeding a state machine for each in-flight query.

## Query processing pipeline

```
  SQL string
 (over HTTP)
      |
      v
+------------+
| Parser     | ANTLR grammar -> AST
+------------+
      |
      v
+------------+
| Analyzer   | StatementAnalyzer + MetadataManager
+------------+
      |
      v
+------------+
| Optimizer  | rules + CBO (StatsCalculator)
+------------+
      |
      v
+------------+
| Fragmenter | PlanFragmenter -> PlanFragments
+------------+
      |
      v
+------------+
| Scheduler  | SplitManager + NodeScheduler
+------------+
      |
      v
Tasks dispatched
  to workers
```

### Parsing

The SQL string passes through an ANTLR grammar that produces an Abstract
Syntax Tree (AST). At this stage the coordinator only understands syntax:
the AST has no notion of which tables exist or what types the columns are.

### Semantic analysis

The StatementAnalyzer consumes the AST and produces a typed, validated
representation. It leans on the MetadataManager to talk to connectors and:

- **Resolve names:** Catalog → schema → table → column lookups.
- **Infer types:** Every expression, function, and aggregation gets a type.
- **Check access:** The query's principal must have permission on each
  referenced table and function.

A failure here means the query is syntactically legal but semantically
broken — unknown table, type mismatch, missing privilege.

### Optimization

The optimizer iterates rule-based rewrites and cost-based search over the
plan, producing a physical plan annotated with how each operator runs.
Statistics from connectors (row counts, NDV, null fraction, min/max) feed
the StatsCalculator, which estimates per-node cardinality and bytes — the
inputs the cost model needs to choose join order, broadcast vs partitioned
joins, and similar decisions.

### Fragmentation

The PlanFragmenter walks the physical plan and inserts exchange operators
wherever data must cross the network. It cuts the plan at these boundaries
into PlanFragments. A PlanFragment contains the operators that can run
independently on a single worker until data needs to leave that worker.

| Exchange    | Role                                           |
|-------------|------------------------------------------------|
| Gather      | Funnel partitioned data back to a single node  |
| Repartition | Shuffle data by hash key for the next stage    |
| Replicate   | Broadcast a small build side to every consumer |

### Scheduling

Scheduling has two parallel tracks:

**Split generation:** The SplitManager asks the connector to enumerate
splits — descriptors for a discrete chunk of data, e.g. a byte range in a
Parquet file or a Kafka partition.

**Task placement:** The NodeScheduler converts each PlanFragment into tasks
on chosen workers. Source stages (those reading splits) prefer workers with
data locality; intermediate stages place tasks based on network topology
and load. An execution policy decides whether stages launch all-at-once or
phased — phased delays downstream stages until upstream ones have produced
data.

## Cluster management

Beyond planning a single query, the coordinator runs the cluster's
control-plane services.

### Discovery

The coordinator embeds a discovery service. Workers send periodic HTTP
heartbeats announcing themselves, their state, and resource utilization.
Nodes that stop heartbeating drop out of the scheduler's pool.

### Query tracking

Every active query lives as a state machine on the coordinator:

```
QUEUED -> PLANNING -> STARTING -> RUNNING -> FINISHING -> FINISHED
                                         \-> FAILED
```

The coordinator aggregates per-task statistics streamed from workers,
exposes them via the REST API, and renders them in the Web UI.

### Memory enforcement

The coordinator tracks each query's memory consumption against per-query
and cluster-wide limits. When the cluster's global memory pool is
exhausted, the OOM killer cancels the largest offender — preventing
distributed deadlock where every worker is waiting on memory that no
query is willing to release.

## Related

- [Architecture](architecture.md) - Coordinator, workers, and connectors
- [Query lifecycle](query-lifecycle.md) - End-to-end phases of a query
- [Query optimization](query-optimization.md) - Rules and CBO choices
- [Connector API](connector-api.md) - Where metadata and splits come from

---

Return to [Trino](_index.md)
