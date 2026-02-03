# Cassandra gossip

In Cassandra, gossip is the peer-to-peer communication protocol that allows
nodes to share state information and build a collective awareness of the
cluster's topology and health. Because Cassandra is masterless, gossip is the
mechanism that ensures every node eventually knows about every other node
without a central authority.

## How gossip works

The protocol is modeled after the way rumors spread in a population. It is an
anti-entropy mechanism that is both efficient and highly resilient.

**Periodic exchange:** Once per second, every node in the cluster initiates a
gossip session with up to three other nodes.

**Recursive sharing:** When Node A gossips with Node B, it doesn't just send its
own info; it sends everything it knows about Nodes C, D, and E as well.

**Exponential propagation:** Because every node is gossiping simultaneously,
information about a new node joining or an existing node failing spreads across
even a massive cluster in a matter of seconds.

## What information is gossiped

Nodes exchange a data structure known as the gossip state, which is composed of
several key elements:

| Component             | Description                                                     |
|-----------------------|-----------------------------------------------------------------|
| **Heartbeat state**   | Version number that increments every second; proves liveness    |
| **Application state** | Tokens, schema version, status (BOOT, NORMAL, LEAVING), rack/DC |
| **Version numbers**   | Every piece of state has a version for conflict resolution      |

If Node A receives info about Node C with a higher version than its local copy,
it updates its local state.

## Failure detection (Phi Accrual Detector)

Gossip is the primary input for Cassandra's failure detection. Instead of using
a simple ping that returns a binary up/down status, Cassandra uses a Phi Accrual
Failure Detector.

**Suspicion vs. certainty:** The detector tracks the intervals between
heartbeats. If heartbeats start arriving late, the Phi value increases.

**Adaptive thresholds:** The system calculates the probability that a node is
down. This allows the cluster to be flexible during periods of network
congestion or GC pauses, avoiding the flapping of nodes being marked down
prematurely.

**Action:** When the Phi value crosses a configured threshold, the node is
marked as down locally, and the coordinator will stop routing queries to it,
instead storing hinted handoffs.

## Seed nodes

To prevent a cluster from splitting into isolated islands of nodes that don't
know about each other, Cassandra uses seed nodes.

**Point of contact:** When a new node joins the cluster, it contacts the seed
nodes listed in its configuration to learn about the rest of the ring.

**Not a master:** Seed nodes are regular nodes; they do not have special
authority or store extra data. Their primary role is to act as a reliable
meeting point for gossip synchronization.

## Why gossip is important

Without a central name node or master, gossip provides:

1. **Cluster discovery:** Automatically finding new nodes
2. **Health monitoring:** Detecting failures in real-time
3. **Schema agreement:** Ensuring all nodes run the same version of table
   definitions
4. **Token metadata:** Keeping the token map updated so coordinators can route
   queries correctly

## Related

- [Query routing](query-routing.md) - How gossip informs routing decisions
- [Fault tolerance](fault-tolerance.md) - How failure detection enables resilience
- [Replication](replication.md) - How hinted handoff uses gossip state

Return to [Cassandra](_index.md)
