# Query termination

Three things end a query before it finishes: a failure, a user
cancellation, or a deadline timeout. Trino handles all three the same
way — the coordinator flips the query into a terminal state and tells
every worker to drop its tasks. Only the recorded cause differs.

## The three entry points

**Failures.** Something inside the cluster goes wrong:

- A worker task throws — operator error, out-of-memory, connector
  exception, malformed data.
- A worker process dies.
- A network call to a worker fails after exhausting retries.
- The cluster runs out of memory and the memory manager kills a query.

Any of these bubbles up to the coordinator and fires a transition to
FAILED.

**Cancellations.** Someone or something asks the query to stop:

- The client issues a DELETE on the query.
- A resource group's kill policy fires.
- The optimizer cancels a stage that is no longer needed (e.g., a
  short-circuited LIMIT).
- The client stops polling, and the abandonment timeout fires —
  classified separately so audit logs distinguish "user killed it"
  from "client vanished."

**Deadlines.** The query has run too long or used too many resources.
Background sweeps on the coordinator check each active query against
its limits — wall-clock, execution time, CPU, scan bytes, planning
time, client poll — and fire a FAILED transition when any threshold is
crossed.

## Teardown is fire-and-forget

When the state machine transitions, the coordinator immediately:

- sends an HTTP DELETE to every worker that owned a task for the query, and
- frees the query's slot in the memory pool and resource group, making
  room for a new query.

It does not wait for the workers to acknowledge. Worker-side cleanup is
asynchronous and best-effort.

Cancellation on the worker is cooperative: the DELETE marks the task
canceled and interrupts its driver threads, but operators only notice
the interrupt flag between pages and at split boundaries. Most check
often, so cancellation is usually fast. A connector stuck in a slow
remote call — a JDBC fetch, an S3 read, a metastore RPC — keeps the
driver thread blocked until the call returns; only then does the
operator notice the cancellation.

This is why a query that "won't die" is almost always a worker stuck
in a non-cancellable native call. The coordinator already considers
the query terminal; the wait is for the worker to notice.

---

Return to [Trino](_index.md)
