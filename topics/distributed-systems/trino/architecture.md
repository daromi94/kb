# Architecture

A Trino cluster has two node roles: a single coordinator and many workers.
Connectors mediate access to external data sources. The cluster is stateless
with respect to user data — all data lives in the sources behind connectors.

## Coordinator

The coordinator handles:

- Accepts client SQL submissions over HTTP.
- Parses, analyzes, and plans queries.
- Tracks worker liveness and load.
- Schedules stages and tasks onto workers.
- Aggregates final results back to the client.

There is one active coordinator per cluster. It does not process data pages
itself; its job is planning and orchestration.

## Worker

Workers do the actual data processing:

- Pull splits (data partitions) from sources via connectors.
- Run pipelines of operators that filter, project, join, and aggregate.
- Exchange intermediate results with peer workers over the network.
- Stream final pages back to the coordinator.

Adding workers scales throughput linearly for most queries, since stages
parallelize across all available workers.

## Connector

A connector is the driver layer for a specific data source. It exposes table
metadata, statistics, and data splits to Trino, and accepts pushed-down
operations (filters, aggregates, sometimes joins) that it translates into the
source's native API or query language.

A single Trino installation runs many connectors simultaneously, each
configured as a catalog. A query references tables by `catalog.schema.table`,
allowing seamless joins across sources.

## Cluster topology

```text
    +---------------------+
    |  Client (CLI/JDBC)  |
    +----------+----------+
               | SQL
               v
    +----------+----------+
    |     Coordinator     | parse, plan, schedule
    +----------+----------+
               | tasks
    +----------+----------+
    v          v          v
+--------+ +--------+ +--------+
| Worker | | Worker | | Worker |
+---+----+ +---+----+ +---+----+
    |          |          |
    v          v          v
    +---------------------+
    |  Connectors         |
    |  (Hive, Iceberg,    |
    |   Postgres, Kafka,  |
    |   MongoDB, ...)     |
    +---------------------+
               |
               v
     External data sources
```

---

Return to [Trino](_index.md)
