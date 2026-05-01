# Execution model

Trino's execution is in-memory, pipelined, multi-threaded, and vectorized.
These four properties together explain why interactive queries return in
seconds where MapReduce-style engines take minutes.

## In-memory processing

Intermediate results never touch disk by default. Stages exchange data over
the network through memory buffers. If a query exceeds the cluster's
configured memory limits, it fails — there is no automatic spill. This is
the trade-off for low latency: no disk I/O between operators, but no
unlimited working set either.

Fault-tolerant execution is the opt-in alternative for batch workloads that
need to spill to durable storage.

## Pipelined execution

Operators do not wait for upstream stages to finish. As soon as one operator
produces a page, the next operator consumes it. Data streams continuously
through the pipeline, so:

- Time-to-first-row is short (results stream as they materialize).
- Worker CPUs stay busy while connectors fetch the next batch.
- Memory pressure is bounded by what is in flight, not by the full
  intermediate dataset.

Compare this to materializing-stage engines, where each stage writes its
full output before the next stage starts.

## Multi-threaded driver model

Each worker runs a pool of threads called drivers. A driver executes one
instance of one pipeline over a stream of splits or input pages. Splits are
work-stolen from a shared queue, so any free driver picks up the next ready
split. This:

- Avoids the overhead of process-per-task scheduling.
- Keeps all CPU cores saturated under mixed workloads.
- Lets one worker run many pipelines from many queries concurrently.

The concurrency unit is the driver, not the JVM process — there is one JVM
per worker.

## Vectorized columnar execution

Pages are the data currency between operators. A page is a columnar batch:
each column is a contiguous block of values for some number of rows
(typically thousands).

Columnar batches enable tight inner loops:

- Operators iterate over a column, not over rows of structs.
- The JIT can vectorize these loops with SIMD instructions.
- Cache lines stay hot for the duration of a column scan.

Combined with runtime bytecode generation, this yields per-query specialized
machine code on the hot path.

## Putting it together

```text
Connector ---> Page ---> Operator ---> Page ---> Exchange ---> Page ---> ...
    ^                       ^                        |
    |                       |                        v
  splits                 one driver            network buffers
                         thread per               (no disk)
                         pipeline
```

## Related

- [Query lifecycle](query-lifecycle.md) - Where pipelines and drivers come from
- [Runtime code generation](runtime-codegen.md) - JIT-compiled operators
- [Fault-tolerant execution](fault-tolerant-execution.md) - When memory-only is too fragile

---

Return to [Trino](_index.md)
