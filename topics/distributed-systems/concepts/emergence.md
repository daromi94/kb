# Emergence

Emergence is what a distributed system does that no single node was
programmed to do. The behavior lives in the interactions between
nodes — messages, retries, timeouts, failure detection — each
following simple rules on a partial view of the cluster. Nodes
are deterministic. The cluster is not.

This is the defining property of distributed engineering: local rules
produce global behaviors, intended and unintended, that no node was
programmed to perform.

## Why behavior emerges

Three conditions force it:

- **Concurrency.** Nodes run independently. There is no shared memory
  and no global clock. Order exists only where the protocol creates it.
- **Partial observability.** Each node sees its neighbors and its
  recent messages. No node holds the global state.
- **Unreliable communication.** Messages are delayed, reordered, or
  dropped. A silent peer looks identical to a slow one.

Local decisions made under these conditions interact at scale to
produce macro-level behavior.

## Positive emergence

Distributed algorithms exploit emergence on purpose. Each node follows
simple rules; the aggregate produces a global property no node
coordinates.

- **Gossip.** Each node periodically forwards its state to a few
  peers. Information reaches the whole cluster in time logarithmic in
  cluster size, with no central broadcaster.
- **Control loops.** Each controller compares observed state to
  desired state on its slice and issues corrections. Independent
  loops together migrate work off failing hardware without a global
  scheduler.
- **Consensus.** In protocols like Raft or Paxos, each node only
  proposes, votes, and counts majorities. The cluster agrees on a
  single sequence of operations, even through partitions and crashes.

The pattern is the same: a local rule that is correct in isolation,
plus a quorum or epidemic structure that lifts it into a global
guarantee.

## Negative emergence

The same interaction structure produces destructive behaviors no node
was designed to exhibit.

- **Cascading failure.** A slow component causes callers to hold
  connections longer, exhausting their pools. Failed health checks
  shift traffic to remaining nodes, which overload in turn. The
  failure walks the dependency graph.
- **Thundering herd.** A popular cache entry expires. Every concurrent
  request misses at once and forwards to the origin, which was sized
  for cache hits.
- **Metastable failure.** A trigger pushes the system into a degraded
  state. A feedback loop built from retries, queues, or fallbacks
  keeps it there after the trigger clears.

The structure is identical: a local action that is correct in
isolation — retry on failure, fall through to the source of truth,
fail a health check when overloaded — becomes pathological when many
nodes take it together.

## Engineering implication

Designing a distributed system is mostly choosing local rules whose
aggregate behavior is the one you want. Two questions shape almost
every decision:

1. What global property does this rule produce when every node follows
   it under load and partial failure?
2. What bounds the blast radius when the property is the wrong one?

Load shedding, concurrency limits, jittered retries, per-tenant
quotas, and circuit breakers exist to answer the second question.
They are not optional features. They are the constraints that stop
locally correct decisions from compounding into a global outage.

## Related

- [Overview](overview.md) - Definition and motivation
- [Metastable failures](metastable-failures.md) - Self-sustaining failure states
- [Blast radius reduction](blast-radius-reduction.md) - Containment through compartmentalization
- [Failure detection at scale](failure-detection-at-scale.md) - Heartbeat topology at scale

---

Return to [Concepts](_index.md)
