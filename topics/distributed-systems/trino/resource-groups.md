# Resource groups

Resource groups are the coordinator's admission gate. Every query is
routed to one group, and the group's limits decide whether the query
runs immediately, waits in a queue, or is rejected outright.

A group does not run queries — it only decides which ones may start.

## Routing

The coordinator matches each submitted query against a rule set keyed
on the user, source application, tags, or query properties. The
matched group is fixed for the query's lifetime.

## Three caps

A group enforces three independent caps. Hitting any one holds the
query in a queue or rejects it.

| Cap            | Behavior at the cap                             |
|----------------|-------------------------------------------------|
| Concurrency    | Extra queries wait in QUEUED                    |
| Queue depth    | Submissions over the queue cap are rejected     |
| Cluster memory | Queries wait even if a concurrency slot is open |

**Concurrency** caps the number of running queries from this group at
once. A queued query consumes no memory or CPU until a running slot
frees up.

**Queue depth** caps how many queries can wait. Without it, a flood
of submissions could grow the coordinator's queue indefinitely; once
the queue is full, new submissions are rejected at the door.

**Cluster memory** caps the aggregate memory of the group's running
queries. A query that would push the group over its memory cap stays
in QUEUED until memory frees, even if a concurrency slot is open.

## Killing running queries

A group can also kill running queries when the cluster runs short on
memory. The cluster memory manager picks one of the over-budget
group's queries based on the configured policy. This and the
cluster-wide out-of-memory killer can both fail a query; whichever
fires first wins.

## Why it matters

Without admission control, a single user submitting many heavy queries
can drown the coordinator's planning threads or exhaust cluster
memory. Resource groups give each tenant its own envelope: queries
that would otherwise compete with the rest of the cluster are queued
within their group, so one heavy workload cannot stall everyone else.

---

Return to [Trino](_index.md)
