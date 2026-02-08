# Failure Detection at Scale

The scale of a cluster changes how heartbeats are managed. The core tension is
between detection speed and network overhead.

## Traffic topology

**Small clusters (3-5 nodes)** use full-mesh or all-to-all heartbeats.
A 5-node cluster generates $n \times (n-1) = 20$ messages per interval,
easily handled by modern networks.

**Large clusters (100+ nodes)** cannot afford a full mesh. A 100-node
cluster would produce 9,900 messages per interval; at 100 ms intervals
that is 99,000 packets/s just for health checks. Gossip or ring
topologies restrict each node to pinging only a few neighbors or a
random subset.

## Strategy comparison

| Aspect          | Small cluster                                | Large cluster                                         |
|-----------------|----------------------------------------------|-------------------------------------------------------|
| **Topology**    | Centralized or full mesh                     | Gossip or ring                                        |
| **Consistency** | High — nodes agree quickly on who is up/down | Eventual — failure info propagates over multiple hops |
| **Accuracy**    | Deterministic binary up/down                 | Probabilistic (phi accrual)                           |
| **Network**     | LAN, low latency and jitter                  | Often WAN/multi-region, high jitter                   |
| **Overhead**    | Minimal                                      | Significant; requires optimization                    |

## False-positive impact

In a small cluster a false positive triggers a leader election involving
3-5 nodes that completes in milliseconds.

In a large cluster a false positive can trigger a massive rebalance. If
the cluster believes a node holding 10 TB of data is dead, it begins
copying that data to other nodes. The resulting bandwidth consumption
slows other heartbeats and can cascade into more nodes being incorrectly
marked dead.

## Convergence time

Small clusters converge almost instantly: every follower notices a
missing heartbeat within the next timeout interval.

Large clusters rely on gossip protocols. When node A dies, neighbor B
notices and tells C and D, who tell others. The information spreads with
a logarithmic infection rate ($O(\log n)$), so the full cluster learns
of the failure after several hops rather than all at once.

## Related

- [Heartbeat](heartbeat.md) - The underlying pattern and timing
  inequality
- [Leader election](leader-election.md) - Recovery action triggered by
  heartbeat failure

---

Return to [Concepts](_index.md)
