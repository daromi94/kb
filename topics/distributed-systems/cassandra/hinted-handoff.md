# Hinted handoff

Hinted handoff is Cassandra's store-and-forward mechanism for writes during
transient node failures. When a target replica is unreachable, the
coordinator stores the write locally and delivers it once the node recovers,
allowing the cluster to maintain write throughput without client retries.

## How hints work

When a write arrives and a replica is unreachable, the coordinator creates a
hint rather than failing the write.

**Hint contents:** The actual data being written, the intended target node's
ID, and a timestamp.

**Storage:** The coordinator stores the hint on its own local disk in the
`hints` directory.

**Delivery:** The coordinator monitors the failed node via the gossip
protocol. Once gossip signals the node is back online (`UP` status), the
coordinator hands off the saved writes.

## Consistency level interaction

Hints do not count toward consistency level acknowledgments for most
settings.

**Standard levels:** A hint ensures durability (the data is on some disk),
but it does not satisfy `ONE`, `QUORUM`, or `ALL`. If `CL.QUORUM` requires
two actual replica acknowledgments and two nodes are down, the write fails
even if hints can be stored.

**The ANY exception:** `CL.ANY` is a special level where the write succeeds
even if only a hint was recorded. This provides maximum write availability,
but the data is not readable until the hint is delivered to a real replica.

## Recovery flood

A significant risk is the thundering herd problem when a node recovers. If a
node is down for several hours, thousands of hints accumulate across the
cluster. When that node comes back, every other node may attempt to flush
hints simultaneously, potentially overwhelming the recovering node.

Cassandra manages this through two constraints:

**Time window:** Hints are stored for a configurable period (default is
typically 3 hours). If a node is down longer than this window, hints are
discarded and the node must be repaired using anti-entropy repair.

**Throttling:** The `HintsService` limits the delivery rate to prevent
flooding the recovering node.

## Summary

| Attribute         | Detail                                                     |
|-------------------|------------------------------------------------------------|
| Primary goal      | Maintain write availability during transient node failures |
| Storage location  | Local disk of the coordinator node                         |
| Delivery trigger  | Gossip status change to `UP`                               |
| CL impact         | Does not satisfy `ONE`, `QUORUM`, or `ALL`                 |
| Expiration        | Configurable time window (default ~3 hours)                |
| Beyond expiration | Anti-entropy repair required                               |

## Related

- [Anti-entropy](anti-entropy.md) - Repair for data missed beyond the hint window
- [Fault tolerance](fault-tolerance.md) - How hinted handoff fits into self-healing
- [Gossip](gossip.md) - How node liveness is detected
- [Consistency](consistency.md) - Tunable consistency levels

---

Return to [Cassandra](_index.md)
