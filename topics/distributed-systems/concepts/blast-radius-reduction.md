# Blast radius reduction

Deciding whether a component should crash or gracefully degrade is hard,
and engineers will inevitably get it wrong. Blast radius reduction
accepts this and compartmentalizes infrastructure so that a wrong
decision takes down a small fraction of users instead of causing a
global outage. The architectural posture is humility in the face of
complexity — the leverage is not in preventing every bad decision but
in bounding its reach.

## Cell-based architecture

A cell is a self-contained stack of compute, storage, and routing that
serves a subset of users end-to-end. Cells share no runtime state, so a
failure — a poison-pill crash loop, a corrupted deployment, a bad config
push — is confined to the cell that produced it.

- Users are mapped to cells by a stable key such as account or tenant
  ID.
- A thin routing layer forwards each request to the correct cell.
- Cells are sized so that losing one affects a known, tolerable fraction
  of traffic, often 1-5%.

The cell boundary replaces trust in correct error handling with physical
isolation.

## Shuffle sharding

Shuffle sharding narrows the reach of a failure further by changing how
tenants land on back-end nodes. Instead of sharing one pool, each tenant
is assigned a small random subset of nodes — its shard. When a poison
pill takes that shard down, only the tenants whose shards overlap with
it are affected.

With $n$ nodes and shards of size $k$ per tenant, the probability that
two tenants share all $k$ nodes drops combinatorially. One bad tenant
rarely brings down any other tenant completely.

## Why it matters for error handling

When the crash-or-continue decision is wrong, the fault fans out along
the same path the request originally took.

- Without compartmentalization, a poison pill fans out across the entire
  fleet and produces a full outage.
- With cells, the fan-out stops at the cell boundary.
- With shuffle sharding, it stops at the intersection of shards.

The failure is not prevented — it is contained. The system can tolerate
imperfect judgment about when to crash, which is the realistic
operating condition of any large codebase.

---

Return to [Concepts](_index.md)
