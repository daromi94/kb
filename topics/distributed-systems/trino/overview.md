# Overview

Trino is a distributed SQL query engine for fast, interactive analytics over
data ranging from gigabytes to petabytes. It has no storage layer of its own;
instead, it provides a unified SQL interface to query data wherever it lives.

## Separation of compute and storage

Trino does not own the data it queries. A connector architecture lets a single
SQL statement read from object storage tables (Hive, Iceberg, Delta Lake on
S3), relational databases (PostgreSQL, MySQL), streaming systems (Kafka), and
document stores (MongoDB) — and join across all of them in one query.

This decoupling means:

- **No ingestion step:** Query data in place; no need to copy it into a
  warehouse first.
- **Federated joins:** Combine sources that otherwise live in isolation.
- **Independent scaling:** Add workers without touching storage.

## Use cases

| Workload          | Why Trino fits                                     |
|-------------------|----------------------------------------------------|
| Lakehouse SQL     | ANSI SQL over Iceberg/Delta tables on object store |
| Federated queries | One query spans multiple heterogeneous sources     |
| Interactive BI    | Sub-second to seconds latency for ad-hoc analysis  |
| ETL (with FTE)    | Long-running batch jobs via fault-tolerant mode    |

## SQL surface

Trino implements ANSI SQL faithfully: window functions, CTEs (recursive and
non-recursive), lateral joins, complex types (arrays, maps, rows), and rich
type coercion. Most analytical SQL written for traditional warehouses runs on
Trino with little or no change.

## When not to use Trino

- Transactional workloads: row-level updates, OLTP, single-record lookups.
- Tiny datasets where a single-node engine suffices.
- Workloads needing strict ACID across multi-statement transactions.

## Related

- [Architecture](architecture.md) - Coordinator and worker roles
- [Connector API](connector-api.md) - How Trino plugs into data sources
- [Execution model](execution-model.md) - In-memory pipelined processing

---

Return to [Trino](_index.md)
