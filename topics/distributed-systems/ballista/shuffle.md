# Shuffle

When a query crosses a stage boundary, data must be repartitioned across
executors. Ballista materializes the upstream stage's output to local
disk in Arrow IPC format, then streams it on demand to downstream
executors over Apache Arrow Flight.

## Why a stage boundary exists

A stage boundary appears where the physical plan changes partitioning:
hash repartition, sort-based merge, broadcast, or a final aggregate that
collapses to one partition. Within a stage, partitioning is invariant
and operators pipeline freely; across a boundary, data must rendezvous
on a different key, so streams can no longer be local.

## Write side

The last operator of a non-final stage is a shuffle writer. For each
partition of input it produces an Arrow IPC file on the executor's
local disk, partitioned by the downstream stage's expected key. Layout
on disk matches the in-memory Arrow layout, so writing is bulk byte
transfer of Arrow buffers — no row-level encoding.

When the task finishes, the executor reports the shuffle file locations
back to the scheduler.

## Read side

A downstream stage's tasks each pull the partitions they own. The
shuffle reader issues Arrow Flight requests (gRPC under the hood) to
each producing executor. The producer streams the Arrow IPC file
contents back; the reader reinterprets the bytes as Arrow record
batches in memory.

Because the wire layout is the in-memory layout, deserialization is a
buffer reinterpretation rather than a per-row decode.

## Why it looks this way

| Choice                            | Consequence                                           |
|-----------------------------------|-------------------------------------------------------|
| Materialize shuffle to disk       | Downstream can retry without rerunning upstream stage |
| Arrow IPC on disk and on the wire | No row-level serde at any boundary                    |
| Flight (gRPC) as transport        | HTTP/2 streaming, mature client libraries             |
| Per-partition files               | Readers fetch only what they own                      |

```text
Upstream stage task                       Downstream stage task
+------------------+                      +------------------+
|  DataFusion ops  |                      |  DataFusion ops  |
|        |         |                      |        ^         |
|        v         |                      |        |         |
|  ShuffleWriter   |                      |  ShuffleReader   |
+--------+---------+                      +--------+---------+
        | Arrow IPC                                ^
        v                                          |
+------------------+  Arrow Flight (gRPC)          |
| Local disk:      |  -------------------------->  |
| part-0.ipc       |  stream Arrow record batches  |
| part-1.ipc       |                               |
| ...              |                               |
+------------------+                               |
```

---

Return to [Ballista](_index.md)
