# Quorum

A quorum is the minimum number of nodes that must agree on an operation
for it to be considered successful. The core idea is **quorum
intersection**: the set of nodes that acknowledge a write must always
overlap with the set of nodes that respond to a read, so at least one
node in every read carries the latest value.

## The quorum formula

Given $n$ replicas, a write quorum $w$, and a read quorum $r$, the
fundamental consistency requirement is:

$$w + r > n$$

The overlapping node acts as a witness that carries the most recent
version of the data. If the inequality does not hold, a read can hit a
set of nodes that never received the latest write, returning permanently
stale data.

## Common configurations

| Configuration   | Rule                                                 | Trade-off                          | Use case                         |
|-----------------|------------------------------------------------------|------------------------------------|----------------------------------|
| Majority quorum | $w = \lceil(n+1)/2\rceil$, $r = \lceil(n+1)/2\rceil$ | Balanced; tolerates $n/2$ failures | Most databases (Cassandra, Riak) |
| Write-heavy     | $w = n$, $r = 1$                                     | Slow writes, fast reads            | Systems with rare updates        |
| Read-heavy      | $w = 1$, $r = n$                                     | Fast writes, slow reads            | Logging or telemetry             |

## Why quorum matters

Without a quorum, a distributed system faces two major risks:

**Split brain.** During a network partition both sides of the split may
accept writes independently, causing data to diverge. Requiring a
majority ($> n/2$) ensures only one partition can form a quorum.

**Stale reads.** When $w + r < n$, it is possible to read exclusively
from nodes that missed the latest write, so the system silently returns
outdated data.

## Strict vs sloppy quorum

**Strict quorum.** Operations succeed only if the designated replica
nodes for that key are reachable. When they are down, the operation
fails. This prioritizes consistency.

**Sloppy quorum (hinted handoff).** When the home nodes are
unavailable, the system writes to any reachable node instead. That
temporary node stores a hint and forwards the data to the intended
replica once it recovers. This prioritizes availability at the cost of
consistency guarantees, since the temporary nodes are outside the
original replica set and the quorum intersection property no longer
holds in the strict sense.

## Quorum does not imply linearizability

The formula $w + r > n$ guarantees overlap but not ordering. In-progress
writes, partial failures, and clock skew can still cause stale or
inconsistent reads. Achieving strong consistency requires additional
mechanisms such as leader-based sequencing, read repair, or consensus
protocols.

## Related

- [Quorum and linearizability](quorum-and-linearizability.md) - Why
  quorum overlap alone does not guarantee strong consistency
- [Replication](replication.md) - Quorum as a replication coordination
  strategy
- [CAP theorem](cap-theorem.md) - The trade-off space quorum
  configurations navigate

---

Return to [Concepts](_index.md)
