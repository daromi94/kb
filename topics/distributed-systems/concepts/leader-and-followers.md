# Leader and Followers

A single node (the leader) accepts all writes and propagates them to
follower nodes. By funneling mutations through one point, the system
establishes a total ordering of operations and avoids conflicting states
that arise when multiple nodes accept writes independently.

## Roles

**Leader** — sole entry point for write requests. Assigns a monotonically
increasing version number (log index) to each operation, appends it to
the local write-ahead log, and replicates the entry to all followers.

**Followers** — receive log entries from the leader and apply them in
order to their local state. Typically serve read traffic to offload the
leader.

## Replication flow

```
Client          Leader                Followers
  |--- write ---->|                       |
  |               |-- append to WAL       |
  |               |   (uncommitted)       |
  |               |                       |
  |               |--- replicate -------->|  (parallel)
  |               |                       |
  |               |<------ ack -----------|  (quorum)
  |               |                       |
  |               |-- mark committed      |
  |<-- success ---|   update high-water   |
```

1. Client sends a write to the leader.
2. Leader appends the entry to its WAL (uncommitted).
3. Leader sends the entry to followers in parallel.
4. Followers write to their own WALs and acknowledge.
5. Once a quorum of nodes acknowledges, the leader marks the entry
   committed.
6. Leader responds to the client and advances the high-water mark.

## Read consistency trade-offs

| Strategy           | Guarantee              | Trade-off                        |
|--------------------|------------------------|----------------------------------|
| Read from leader   | Strong consistency     | Leader becomes a read bottleneck |
| Read from follower | Higher read throughput | Risk of stale reads              |

Reading from a follower that has not yet received the latest entry from
the leader produces a stale read. Systems that need linearizable reads
must either route them through the leader or use additional coordination.

## Key challenges

**Split brain.** A network partition may cause two nodes to believe they
are both leader. Generation clocks and quorum requirements ensure only
one leader can actually commit writes.

**Write latency.** In synchronous replication the leader's performance
is bounded by the slowest node in the quorum.

**State transfer.** When a follower joins or recovers after a crash, it
must catch up on missed log entries. This typically involves replaying
from the segmented log, guided by the low-water mark to determine
where to start.

## Related

- [Replication](replication.md) - Broader strategies including
  multi-leader and leaderless approaches
- [Leader election](leader-election.md) - How a leader is chosen and
  replaced after failure
- [Write-ahead log](write-ahead-log.md) - The log structure that
  underpins the replication flow
- [Low-water mark](low-water-mark.md) - Determines the safe boundary
  for log cleanup and follower catch-up
- [Quorum and linearizability](quorum-and-linearizability.md) - Why
  quorum overlap alone does not guarantee strong consistency

---

Return to [Concepts](_index.md)
