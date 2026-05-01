# Query optimization

Trino uses a cost-based optimizer (CBO) on top of rule-based rewrites. The
optimizer's job is to turn a logically correct plan into one that minimizes
data movement and CPU work, given what the connectors know about the data.

## Cost-based optimization

The CBO compares candidate plans using statistics returned by connectors:

- Row counts per table.
- Distinct value counts (NDV) per column.
- Null fractions.
- Data size (bytes) per column or partition.

From these it estimates per-operator output sizes and picks the cheapest
plan. Without statistics, it falls back to heuristics — usually a worse
plan, especially for queries with multiple joins.

## Major optimizations

### Predicate pushdown

Filters move as close to the scan as possible, ideally into the connector
itself so the source evaluates them. A `WHERE region = 'EU'` against a Hive
table becomes a partition prune; against PostgreSQL, the connector embeds
it in the SQL statement.

### Projection pushdown

Only the columns the query needs are read. Critical for columnar formats
(Parquet, ORC) where unread columns cost nothing.

### Join reordering

The optimizer reorders join trees to keep intermediate results small.
A simple rule: filter and probe the largest table last. Statistics drive
this — accurate row counts let the CBO put the smaller side on the
build side of a hash join.

### Join strategy selection

| Strategy    | When chosen                          | Cost                       |
|-------------|--------------------------------------|----------------------------|
| Broadcast   | One side is small                    | Replicate small to workers |
| Partitioned | Both sides are large                 | Shuffle both by join key   |
| Co-located  | Both sides already partitioned alike | No shuffle                 |

Broadcast avoids shuffling the large side; partitioned (also called shuffle
or repartitioned) is the fallback when neither side is small.

## Rule-based rewrites

Alongside the CBO, a library of deterministic rules simplifies the plan:
constant folding, predicate simplification, subquery decorrelation,
redundant projection removal, exchange elimination. These run repeatedly
until the plan stabilizes.

## Related

- [Connector API](connector-api.md) - Where statistics and pushdown come from
- [Query lifecycle](query-lifecycle.md) - When optimization happens
- [Execution model](execution-model.md) - How chosen plans actually run

---

Return to [Trino](_index.md)
