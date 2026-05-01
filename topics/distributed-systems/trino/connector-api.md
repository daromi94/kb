# Connector API

Connectors are how Trino reads from external data sources. Each connector
implements a small set of interfaces that together let Trino plan and execute
queries against the source as if it were native SQL storage.

## Three core APIs

| API           | Provides                               | Used during      |
|---------------|----------------------------------------|------------------|
| Metadata      | Schemas, tables, columns, types        | Parsing/analysis |
| Statistics    | Row counts, NDV, sizes, null fractions | Optimization     |
| Data location | Splits and the workers to assign them  | Scheduling       |

### Metadata API

Returns the catalog's structure: which schemas exist, which tables they
contain, and what columns and types each table has. The analyzer uses this
to validate the query — every referenced table and column must resolve, and
types must be compatible.

### Statistics API

Returns cost information so the optimizer can compare alternative plans.
Without statistics, the optimizer falls back to heuristics (often producing
worse plans, especially for joins).

### Data location API

Splits are the unit of parallelism: a split is a chunk of data a single task
can read independently. The connector enumerates splits for a table and tells
the coordinator which workers should process which splits — typically
preferring data-local workers when the source supports locality hints.

## Pushdown

Connectors can implement pushdown to delegate work back to the source rather
than streaming all data into Trino:

- **Filter pushdown:** `WHERE` predicates execute in the source.
- **Projection pushdown:** Only requested columns are read.
- **Aggregate pushdown:** `COUNT`, `SUM`, `GROUP BY` evaluated at the source.
- **Join pushdown:** Some connectors push joins down when both sides live in
  the same source (e.g., two tables in the same PostgreSQL database).

Pushdown is the difference between a fast query and one that drags the entire
table across the network.

## Federation

Each connector is configured as a catalog. Tables are addressed as
`catalog.schema.table`, and a single query can join across catalogs:

```sql
SELECT
  u.name, o.total
FROM
  postgres.public.users u
JOIN
  hive.sales.orders o
ON
  u.id = o.user_id
WHERE
  o.region = 'EU';
```

The coordinator plans the join, pushes the region filter into the Hive
scanner, fetches matching rows from both sources in parallel, and joins on a
worker. The user sees one logical SQL surface across heterogeneous storage.

## Related

- [Architecture](architecture.md) - How connectors fit into the cluster
- [Query optimization](query-optimization.md) - How statistics drive planning
- [Query lifecycle](query-lifecycle.md) - Where splits enter scheduling

---

Return to [Trino](_index.md)
