# Quorum and linearizability

The quorum rule ($W + R > N$) guarantees that the set of nodes
acknowledging a write and the set responding to a read always overlap.
This ensures overlap, not timing. For strong consistency
(linearizability) — where the system behaves as if there is a single
copy of the data and all operations are atomic — quorum alone is not
enough.

## In-progress writes cause stale reads

Even with $W=2, R=2, N=3$, a read can return stale data while a write
is propagating.

1. A client writes key X from `1` to `2`.
2. Node A stores `2`. Node B has not received the update yet.
3. A second client reads from Node B and Node C. Both still hold `1`.
4. The read returns `1` despite the write to Node A being initiated
   first.

Because the system does not block reads until the write is committed
across the quorum, two clients can observe different values at the same
time.

## Failed writes leave ghost data

A write that partially succeeds can leave inconsistent state that
simple quorum reads cannot resolve.

1. A write targets a quorum of 2 out of 3 nodes.
2. It succeeds on Node A but fails on Node B due to a network glitch.
   The client receives a failure response.
3. The data still sits on Node A. A future reader hitting Node A and
   Node C may pick up the "failed" value through last-write-wins
   resolution, making a write the client believed failed become
   visible.

## Non-atomic reads violate ordering

Strong consistency requires that once a read returns a new value, all
subsequent reads return that value or a newer one. Without read repair:

1. Client 1 reads from a quorum and sees a mix of old and new values.
   It identifies the new value as the winner.
2. Client 2 reads from a different overlapping quorum a moment later.
   Due to network timing, it sees a majority of old values and
   concludes the old value wins.
3. The system has flipped back to an older state, violating
   linearizability.

## Achieving strong consistency

Moving from eventual consistency to linearizability requires additional
mechanisms on top of quorum overlap:

- **Leader-based sequencing** — a single leader assigns a global order
  to every operation, preventing concurrent writes to the same key
- **Read repair** — the reader writes the winning value back to all
  quorum nodes before returning the result
- **High-water mark** — data is only visible to readers after it has
  been replicated to a majority
- **Consensus protocols (Raft/Paxos)** — use quorums internally but
  add terms and commit indexes to make committed values irrevocable

## Summary

| Property         | Quorum ($W+R > N$)                      | Linearizability                             |
|------------------|-----------------------------------------|---------------------------------------------|
| Visibility       | New data appears eventually             | New data visible to all atomically          |
| Concurrency      | Reads can overlap with in-flight writes | Operations appear in a strict total order   |
| Failure handling | May surface partially written data      | Only returns committed data                 |
| Performance      | Low latency                             | Higher latency from additional coordination |

## Related

- [Quorum](quorum.md) - The intersection rule, configurations, and
  strict vs sloppy quorum
- [Replication](replication.md) - Quorum is one of several replication
  coordination strategies
- [Leader and followers](leader-and-followers.md) - Leader-based
  sequencing as a path to linearizability
- [CAP theorem](cap-theorem.md) - The consistency guarantee that
  linearizability formalizes

---

Return to [Concepts](_index.md)
