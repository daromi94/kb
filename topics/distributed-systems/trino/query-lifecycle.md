# Query lifecycle

A SQL statement passes through a fixed sequence of phases on the coordinator
before any worker touches data. Each phase produces a more concrete
representation of the work to be done.

## Phases

```
  SQL text
     |
     v
+-----------+        +----------+        +--------------+
| Parse and | -----> | Plan and | -----> | Schedule     |
| analyze   |        | optimize |        | onto workers |
+-----------+        +----------+        +--------------+
                                                |
                                                v
                                         Workers execute
```

### 1. Parse and analyze

The SQL text is parsed into an Abstract Syntax Tree (AST). The analyzer
resolves names against connector metadata, type-checks expressions, and
rewrites references into fully qualified form. Errors here are syntactic or
semantic — invalid SQL, unknown tables, type mismatches.

### 2. Plan and optimize

The AST is lowered to a logical plan: a tree of relational operators
(`Scan`, `Filter`, `Project`, `Join`, `Aggregate`). The optimizer rewrites
this tree using rules and a cost-based search:

- Predicate and projection pushdown into scans.
- Join reordering based on table statistics.
- Choice of physical join strategy (broadcast vs partitioned/shuffle).
- Insertion of exchanges between operators that need redistribution.

The result is a physical plan annotated with how each operator runs and how
data flows between them.

### 3. Schedule

The physical plan is split at exchange boundaries into stages.

| Concept  | Definition                                                |
|----------|-----------------------------------------------------------|
| Stage    | Plan fragment between exchanges; runs across many workers |
| Task     | One stage's work on one worker                            |
| Pipeline | Linear chain of operators within a task                   |
| Driver   | Thread executing one pipeline instance over splits        |
| Operator | Single relational op (filter, hash-join, aggregate, etc.) |
| Page     | Columnar batch of rows flowing between operators          |

Stages form a DAG: leaf stages read from connectors, intermediate stages
shuffle between workers, the root stage returns results to the coordinator.

### 4. Execute

Each worker runs its assigned tasks. Drivers pull pages through their
operator pipeline. Pages cross stage boundaries via exchange operators that
move data over the network. Results stream back to the coordinator and out
to the client as soon as they are ready — there is no "wait until the whole
query finishes" step.

## Why the hierarchy matters

Stages → tasks → pipelines → drivers → operators → pages is the unit of work
at every level of granularity. Concurrency, scheduling, memory accounting,
and back-pressure all hook into this hierarchy.

## Related

- [Architecture](architecture.md) - Coordinator and worker roles
- [Query optimization](query-optimization.md) - What the optimizer decides
- [Execution model](execution-model.md) - How drivers and pages run

---

Return to [Trino](_index.md)
