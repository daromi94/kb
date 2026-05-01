# Query tracker

The query tracker is the coordinator's in-memory registry of every query
the cluster knows about — running, queued, recently finished, or failed.
It owns each query's lifecycle state, and anything that needs to find a
query by ID — the REST endpoints serving clients, the web UI, the memory
killer, event listeners — goes through the tracker.

The tracker is per-coordinator state. Nothing is replicated across
coordinators or persisted to disk: a coordinator restart wipes the
registry, and any in-flight queries die with it.

## State machine

Every tracked query owns a state machine that moves forward through a
fixed sequence:

| State     | Meaning                                                 |
|-----------|---------------------------------------------------------|
| QUEUED    | Held by resource group admission control                |
| PLANNING  | Parser, analyzer, and CBO are running                   |
| STARTING  | Plan fragmented; scheduler dispatching tasks to workers |
| RUNNING   | At least one task is processing data                    |
| FINISHING | Computation done; results buffered for the client       |
| FINISHED  | Terminal — completed successfully                       |
| FAILED    | Terminal — error or limit hit                           |
| CANCELED  | Terminal — user-initiated cancel                        |

Transitions are forward-only and serialized inside the state machine,
with listener callbacks firing on every change. This is how the tracker
detects terminations and how audit plugins observe each query's
lifecycle.

## What an entry holds

Each tracker entry is a query execution object that wraps:

- The state machine.
- The session (user, catalog, schema, properties, transaction ID).
- The scheduler that drives stage and task execution.
- Memory accounting handles.
- Result buffers for the root stage.
- Timing, statistics, and error info.

The tracker itself does not run queries — it holds these references and
enforces lifecycle policies.

## Responsibilities

### Lookup and registration

A concurrent map keyed by query ID. Queries are registered once dispatch
decides this coordinator will run them, and lookup is lock-free.

### Status aggregation

The tracker pulls task status from workers rather than receiving pushes.
For each running task it long-polls the worker's status endpoint: the
request says, in effect, "tell me when this task's status changes, or in
one second, whichever comes first." Each response carries CPU time,
memory in use, rows processed, and per-task state, which the tracker
aggregates into the QueryInfo the UI and clients read.

The pull model bounds coordinator load: it decides how many tasks to
poll concurrently instead of being swamped by every worker pushing at
once.

### Expiration of finished queries

A background sweep evicts terminated queries when two limits are both
exceeded:

- A minimum age before a finished query becomes eligible for removal
  (typically 15 minutes), so clients can still fetch results after the
  query technically finished.
- A maximum number of finished queries to retain (typically 100).

Once evicted, the only persistent record is whatever the event-listener
plugin wrote at completion.

### Limit enforcement

A separate sweep kills active queries that exceed their configured
limits:

| Limit               | What it bounds                            |
|---------------------|-------------------------------------------|
| Wall-clock run time | Total time from submission to finish      |
| Execution time      | Time spent specifically in RUNNING        |
| CPU time            | Aggregate CPU consumed across workers     |
| Client timeout      | Time since the client last polled results |

Crossing any limit transitions the query to FAILED with an error code
and cancels every running task. The client timeout matters most in
practice — without it, a disconnected client would leave a zombie query
holding cluster resources indefinitely.

### Distributed teardown

When a query reaches a terminal state, the tracker broadcasts DELETE
requests to every worker that ran a task for it. Workers stop their
drivers, release memory, and drop spilled data. The tracker then
notifies its event-listener plugins (for audit logs and external
monitoring) before retiring the entry from the active set.

## Per-coordinator scope

Query IDs are meaningful only on the coordinator that issued them. In a
multi-coordinator deployment, a gateway pins each session to one
coordinator — a client that routes to a different coordinator mid-query
gets a lookup failure. There is no shared store, no replication, no
cluster-wide query registry.

## Related

- [Coordinator deep dive](coordinator-deep-dive.md) - Other coordinator subsystems
- [Discovery service](discovery-service.md) - The other coordinator-side registry
- [Query lifecycle](query-lifecycle.md) - End-to-end phases of a query

---

Return to [Trino](_index.md)
