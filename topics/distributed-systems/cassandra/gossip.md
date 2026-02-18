# Gossip

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

## Three-way handshake

Rather than broadcasting full state, nodes exchange only deltas through a
Syn-Ack-Ack2 handshake:

| Message          | Sent by   | Content                                               |
|------------------|-----------|-------------------------------------------------------|
| GossipDigestSyn  | Initiator | List of known nodes with their latest version numbers |
| GossipDigestAck  | Recipient | Newer data for initiator + request for missing data   |
| GossipDigestAck2 | Initiator | Requested data to complete the sync                   |

The Syn message is small — just node IDs and version numbers, not full
state. The recipient compares versions, sends back anything newer it has,
and requests anything the initiator has that is newer. After the third
message, both nodes are synchronized.

This delta-based approach keeps bandwidth low even in large clusters. If
messages are lost, the next one-second cycle triggers a fresh handshake
that catches up automatically.

## Versioning and convergence

Every piece of gossip state (status, tokens, schema version) carries a
monotonically increasing version number. When two nodes disagree, the
higher version wins. Because every node gossips with several peers each
second, information propagates exponentially — even a 1,000-node cluster
converges within seconds of a state change.

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

## Failure detection

Gossip heartbeats are the primary input for failure detection. Rather than
a binary up/down check, Cassandra uses the Phi Accrual Failure Detector,
which tracks heartbeat arrival intervals and calculates a probabilistic
suspicion level. When the suspicion crosses a threshold, the node is
convicted and the coordinator stops routing queries to it.

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

- [Phi accrual failure detector](phi-accrual.md) - Deep dive on probabilistic failure detection
- [Topology](topology.md) - The cluster hierarchy gossip propagates
- [Query routing](query-routing.md) - How gossip informs routing decisions
- [Fault tolerance](fault-tolerance.md) - How failure detection enables resilience
- [Replication](replication.md) - How hinted handoff uses gossip state

---

Return to [Cassandra](_index.md)
