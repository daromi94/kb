# Snitch

The snitch bridges the logical ring with the physical network. It maps IP
addresses to a hierarchy of data centers and racks, enabling Cassandra to
make topology-aware decisions about replica placement and query routing.

## Why topology matters

The snitch mapping serves two purposes:

**Safety (replication):** Prevents Cassandra from placing all replicas on the
same physical rack, which would share a single point of failure such as a
power supply or network switch.

**Efficiency (routing):** Allows a coordinator to prefer replicas in the same
rack or data center, avoiding the latency cost of cross-regional network
hops.

## Static snitches

Static snitches define the base topology map from configuration or cloud
metadata.

| Snitch                      | Behavior                                             |
|-----------------------------|------------------------------------------------------|
| SimpleSnitch                | Topology-unaware default; single-DC development only |
| GossipingPropertyFileSnitch | Local config shared via gossip; production standard  |
| Cloud-specific (EC2, GCP)   | Auto-detects region/AZ from provider metadata API    |

## Dynamic snitch

The `DynamicEndpointSnitch` wraps the configured static snitch and adds
real-time performance awareness.

**Latency scoring:** It scores nodes based on latency (EWMA) and severity
(background task pressure) to route requests to the best performing
replica. If a physically closer node starts performing significantly
worse than a distant one (due to compaction, disk I/O spikes, etc.), the
dynamic snitch temporarily routes traffic away from the busy node.

**Periodic reset:** Scores are reset on a regular interval so a node is not
permanently penalized for a transient performance dip.

## Optimized reads

The snitch is most visible during read operations. When a coordinator needs
to satisfy a consistency level, it does not pick replicas at random:

1. **Identify replicas:** Find all nodes holding the requested partition.
2. **Sort by proximity:** The snitch ranks replicas from closest to farthest.
3. **Full-data read:** Send a request for the complete data to the
   fastest/closest replica (selected by the dynamic snitch).
4. **Digest reads:** Send lightweight hash-only requests to the remaining
   required replicas to verify consistency.

By requesting full data only from the healthiest, closest node, Cassandra
minimizes network transfer and reduces overall query latency.

## Static vs dynamic comparison

| Aspect  | Static snitch                   | Dynamic snitch                    |
|---------|---------------------------------|-----------------------------------|
| Input   | Manual config or cloud metadata | Real-time latency and node health |
| Purpose | Define rack/DC boundaries       | Optimize for lowest latency       |
| Impact  | Replica placement (safety)      | Query routing (performance)       |

## Related

- [Topology](topology.md) - Nodes, racks, data centers, and the snitch
- [Query routing](query-routing.md) - How the coordinator dispatches requests
- [Phi accrual failure detector](phi-accrual.md) - Scoring model used by dynamic snitch

---

Return to [Cassandra](_index.md)
