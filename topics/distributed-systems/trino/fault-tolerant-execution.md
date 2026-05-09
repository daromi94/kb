# Fault-tolerant execution

Trino's default execution model is in-memory and all-or-nothing: any worker
crash, network blip, or out-of-memory condition fails the entire query.
That is acceptable for interactive queries that finish in seconds, but
fragile for batch ETL jobs that run for hours.

Fault-tolerant execution (FTE) adds optional retry and spool support so
long-running queries survive worker failures.

## What changes under FTE

| Aspect            | Default (in-memory)         | Fault-tolerant             |
|-------------------|-----------------------------|----------------------------|
| Exchange data     | Streamed via memory buffers | Spooled to durable storage |
| On worker failure | Whole query fails           | Failed tasks/stages retry  |
| Retry granularity | None                        | Task-level or query-level  |
| Latency           | Seconds                     | Higher (spool overhead)    |
| Memory ceiling    | Cluster memory              | Bounded by spool storage   |

## Spooled exchanges

Without FTE, exchange operators move pages directly between workers over
the network. A failed worker means its in-flight pages are gone, and any
downstream stage that consumed them must restart from the source.

With FTE, exchange data is written to a durable spool — typically S3, GCS,
or HDFS — keyed by stage and partition. Downstream stages read from spool
rather than from the producing worker. If a producer fails after writing
its partition, the partition is still readable by consumers; if it failed
before writing, only that task's input range needs to be retried.

## Retry policies

- **Task retry:** Individual failed tasks are re-scheduled. Cheaper, but
  requires deterministic operators.
- **Query retry:** The entire query restarts. Simpler, but wastes prior
  work.

Task retry is the practical choice for ETL because it survives the kinds
of transient failures (preempted spot instances, OOMs on a single worker)
that would otherwise abort hours of work.

## When to enable FTE

Enable for:

- Long-running batch and ETL queries.
- Workloads on cheap, preemptible infrastructure (spot instances).
- Queries with working sets that exceed cluster memory.

Leave disabled for interactive queries: the spool round-trip is not worth
the latency.

---

Return to [Trino](_index.md)
