# Architecture

A Ballista cluster has two long-running process types: schedulers and
executors. Clients connect from outside the cluster to submit work.
Control-plane traffic flows over gRPC with Protocol Buffers; data-plane
traffic flows over Apache Arrow Flight in Arrow IPC format.

## Scheduler

The scheduler accepts query submissions, plans them, and orchestrates
execution. Per query it:

- Receives a logical plan (or SQL text from Flight SQL clients).
- Runs DataFusion's optimizer to produce a physical plan.
- Decomposes the physical plan into stages at partitioning boundaries.
- Tracks executor liveness via heartbeats and assigns tasks to them.
- Streams final results back to the submitting client.

The scheduler does not process row data. It owns planning, scheduling,
and metadata only. Multiple scheduler processes can run for availability;
executor registry and query graph state can be persisted for failover.

## Executor

Executors do the data work. Each executor:

- Registers with the scheduler on startup, then heartbeats and polls
  for tasks.
- Receives physical plan fragments (one task per partition) over gRPC.
- Reads source data via DataFusion table providers (Parquet, CSV,
  object stores).
- Writes per-partition shuffle output as Arrow IPC files on local disk.
- Serves Arrow Flight requests for shuffle output that downstream
  stages need to read.

Adding executors scales throughput because tasks within a stage run in
parallel across all available executors.

## Cluster topology

```text
+----------------------+ +---------------------+
|  Rust/Python client  | |  Flight SQL client  |
+-------+--------------+ +---------+-----------+
        | logical plan             | SQL
        | (protobuf/gRPC)          | (Flight SQL)
        v                          v
        +-------------+------------+
                      |
                      v
             +--------+-------+
             |    Scheduler   |
             |  plan, stage,  |
             |  schedule      |
             +--------+-------+
                      | tasks (gRPC)
          +-----------+-------------+
          v           v             v
     +----+---+   +---+----+   +----+---+
     |Executor|<->|Executor|<->|Executor|
     +----+---+   +---+----+   +----+---+
        shuffle reads via Arrow Flight
          |           |             |
          v           v             v
          +-----------+-------------+
          |  Object store / files   |
          |  (Parquet, CSV, ...)    |
          +-------------------------+
```

---

Return to [Ballista](_index.md)
