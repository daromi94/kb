# Resource groups

Resource groups are the coordinator's admission gate. Every submitted
query is routed to one group, which controls how many queries from
that group can run, how deep its queue can grow, and how much cluster
memory it can collectively consume.

A group has no execution machinery of its own — it is a budget that
gates queries before they reach the query tracker.

## Routing

When a query is submitted, the coordinator matches it against rules
based on the user's identity, source application, tags, or query
properties, and assigns it to a group. The match is deterministic and
fixed for the query's lifetime.

Groups can nest. A child group's limits are evaluated alongside its
parents' — a query has to fit in every level above it before it can
run.

## Limits

Each group enforces three kinds of cap:

| Limit          | What happens at the cap                        |
|----------------|------------------------------------------------|
| Concurrency    | Excess queries are held in QUEUED              |
| Queue depth    | Excess queries are rejected at submission      |
| Cluster memory | Queries wait for memory even if a slot is free |

**Concurrency.** A hard cap on how many queries from this group can
be RUNNING at once. The cap-plus-first query is held QUEUED without
consuming memory or CPU until a slot frees up.

**Queue depth.** Bounds the QUEUED set. When both the running and
queued caps are full, new submissions are rejected immediately so the
coordinator's own memory does not grow unboundedly.

**Cluster memory.** The aggregate memory used by the group's running
queries. A query that would push the group over its memory cap stays
QUEUED, even if a concurrency slot is open.

## Killing running queries

A group can be configured to kill running queries when cluster memory
pressure spikes. The memory manager picks a target from the offending
group based on the configured policy. This intersects with the
cluster's global out-of-memory killer — both can fail a query, and
whichever transition lands first wins.

## Why it matters

Without admission control, a single user submitting many heavy queries
can swamp the coordinator's planning queue or exhaust cluster memory.
Resource groups make capacity multi-tenant: each group has its own
envelope, and queries that would otherwise compete are queued within
their group instead of dragging on every other query in the cluster.

## Related

- [Query tracker](query-tracker.md) - The registry queries enter once admitted
- [Query termination](query-termination.md) - Where memory-killer paths converge
- [Coordinator deep dive](coordinator-deep-dive.md) - Other coordinator subsystems

---

Return to [Trino](_index.md)
