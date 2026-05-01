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

The scheduler does not process data pages. It owns planning, scheduling,
and metadata only. Multiple scheduler processes can run for availability;
state (executor registry, query graph) sits behind a configurable
backend.

## Executor

Executors do the data work. Each executor:

- Registers with the scheduler on startup, then heartbeats and polls
  for tasks.
- Receives physical plan fragments (one task per partition) over gRPC.
- Reads source data through DataFusion (Parquet, CSV, etc., often via
  an object store).
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

## Related

- [Overview](overview.md) - What Ballista is and where it fits
- [Query lifecycle](query-lifecycle.md) - From submission to result
- [Shuffle](shuffle.md) - How partitions move between stages

---

Return to [Ballista](_index.md)
