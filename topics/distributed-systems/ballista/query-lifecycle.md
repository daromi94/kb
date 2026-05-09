# Query lifecycle

A query passes through five phases: plan generation, stage decomposition,
task distribution, execution with shuffle, and result return. The
scheduler owns the first three; executors do the fourth; the scheduler
streams the result back to the client.

## 1. Plan generation

The client builds a logical plan with DataFusion — either by parsing SQL
or by composing DataFrame operations. Rust and Python clients serialize
that logical plan to Protocol Buffers and send it to the scheduler over
gRPC. Flight SQL JDBC clients skip this step and send raw SQL text; the
scheduler then parses and plans on their behalf.

## 2. Stage decomposition

The scheduler runs DataFusion's optimizer to produce a physical plan,
then walks it to find pipeline breakers — operations where partitioning
must change. Aggregations across all rows, hash joins, and explicit
repartitions all force this. Each contiguous run of operators that
preserves partitioning becomes a stage; pipeline breakers become stage
boundaries.

Stages form a DAG. A stage cannot start until all stages it depends on
have produced their shuffle output.

## 3. Task distribution

Each stage is split into tasks, one per partition. Executors poll the
scheduler for work; the scheduler assigns tasks based on registered
executor capacity. The task payload is a serialized physical plan
fragment plus partition identifiers, encoded in protobuf and sent over
gRPC.

## 4. Execution and shuffle

The executor runs the physical plan fragment through DataFusion. For a
non-final stage, the fragment ends in a shuffle writer that materializes
output as Arrow IPC files on local disk, partitioned for the downstream
stage. The executor reports completion to the scheduler, including
where the shuffle output lives.

When a downstream stage starts, its tasks read upstream output through
Arrow Flight requests issued against the producer executors. Because
shuffle output is on disk, an executor failure mid-stage only loses
that executor's tasks — the scheduler can reschedule them.

## 5. Result return

The final stage streams its output back to the scheduler, which streams
it on to the client. There is no cluster-side materialization of final
results.

---

Return to [Ballista](_index.md)
