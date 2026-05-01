# Overview

Ballista is a distributed compute platform for running SQL and DataFrame
queries across a cluster. It is built in Rust, executes plans with
DataFusion, and uses Apache Arrow as the in-memory format from leaf scans
through to network transport.

## Premise

A Ballista cluster runs scheduler and executor processes. Queries are
planned by DataFusion, decomposed by the scheduler into stages, and run
in parallel on executors. Stages communicate by shuffling Arrow record
batches over Apache Arrow Flight.

Two design choices follow from this:

- **One columnar layout end-to-end.** DataFusion operates on Arrow
  in-memory; shuffle files use Arrow IPC; Flight transports Arrow IPC.
  No row-level encode/decode is needed when data crosses a stage
  boundary.
- **Native compilation.** A Rust runtime avoids the latency variance of
  garbage-collected execution for CPU-bound analytical work.

## What runs on it

| Workload                                           | Fit                                    |
|----------------------------------------------------|----------------------------------------|
| Interactive SQL over Parquet/CSV in object storage | Primary use case                       |
| DataFrame jobs that shuffle across many nodes      | Primary use case                       |
| Embedding distributed compute in a Rust/Python app | First-class — local SessionContext API |
| BI tools speaking Arrow Flight SQL (JDBC)          | Supported via Flight SQL endpoint      |

## Related

- [Architecture](architecture.md) - Scheduler, executor, and client roles
- [Query lifecycle](query-lifecycle.md) - From submission to result
- [Shuffle](shuffle.md) - How partitions move between stages

---

Return to [Ballista](_index.md)
