# Leader election

The mechanism by which a cluster chooses a single node to act as
coordinator. When the current leader fails, the cluster must
automatically agree on a successor to maintain the total ordering of
operations.

## Failure detection

The leader sends periodic heartbeat messages to followers. Each follower
maintains an election timeout; if no heartbeat arrives before the timer
expires, the follower assumes the leader has failed and transitions to
candidate state.

Timeouts are randomized to prevent every node from starting an election
simultaneously, which would cause repeated split votes.

## Generation clock

Every election increments a monotonically increasing counter called a
**term** (Raft) or **epoch** (Kafka, ZooKeeper). Any message carrying
a stale term is rejected, which prevents a zombie leader that was
temporarily partitioned from issuing commands after a new leader has
been elected. This is the primary defense against split brain.

## Native election

In protocols like Raft or Paxos, nodes run the election themselves:

1. A candidate increments its term and sends vote requests to all peers.
2. A follower only votes for a candidate whose log is at least as
   up-to-date as its own, preventing a node that missed recent entries
   from becoming leader and losing committed data.
3. A candidate becomes leader when it receives votes from a quorum
   ($\lfloor n/2 \rfloor + 1$).
4. The new leader immediately sends heartbeats to announce authority
   and reset election timers.

**Split votes.** If multiple candidates start simultaneously and none
reaches a majority, all wait for their randomized timeout to expire.
One node will likely time out first in the next round, start a new
election with a higher term, and win.

## Election via consistent core

Many systems outsource leader election to a small, dedicated coordination
cluster (ZooKeeper, etcd, Consul) that provides a linearizable key-value
store with leases and watchers.

1. Every application node races to create a key (e.g. `/service/leader`)
   in the coordination store. Atomic creation guarantees only one
   succeeds.
2. The winner attaches a lease (TTL) to the key and renews it with
   periodic heartbeats.
3. If the leader crashes or is partitioned, the lease expires and the
   store deletes the key.
4. Followers watch the key and immediately race to recreate it when
   it disappears.

**Fencing tokens.** A stalled leader (e.g. long GC pause) might miss
its lease renewal while still believing it is leader. To prevent it
from corrupting data, the coordination store issues a monotonically
increasing fencing token with each new election. The storage layer
rejects any write carrying a token lower than the current one.

## Comparison

| Aspect     | Native (Raft/Paxos)                  | Consistent core (ZooKeeper/etcd)           |
|------------|--------------------------------------|--------------------------------------------|
| Complexity | High — consensus embedded in the app | Low — uses an external API                 |
| Overhead   | Grows with cluster size              | Fixed — core size independent of app size  |
| Dependency | None                                 | Requires maintaining a separate cluster    |
| Best for   | Databases and core infrastructure    | Microservices and distributed applications |

## Related

- [Leader and followers](leader-and-followers.md) - The pattern that
  depends on having an elected leader
- [Replication](replication.md) - Replication strategies that rely on
  leader coordination
- [Segmented log](segmented-log.md) - Log completeness checks during
  voting use the replicated log

---

Return to [Concepts](_index.md)
