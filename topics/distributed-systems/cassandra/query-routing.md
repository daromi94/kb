# Cassandra query routing

Query routing in Cassandra is a decentralized process that ensures any node in
the cluster can handle any request. When a client application executes a query,
the system follows a specific path to locate the data and fulfill the
consistency requirements.

## The coordinator role

The process begins when a client (using a Cassandra driver) connects to any node
in the cluster. This node becomes the coordinator for that specific operation.

**Responsibility:** The coordinator acts as the traffic cop. It manages the
lifecycle of the request, communicates with replicas, and collates the results
before sending them back to the client.

**Intelligence:** The coordinator uses its internal token map to identify
exactly which nodes are the replicas for the specific partition key being
queried.

## Locating the data

Because every node participates in the gossip protocol, every node has a local
copy of the cluster's topology and health.

1. **Hashing:** The coordinator hashes the partition key from the query to
   generate a token.
2. **Ring lookup:** It compares that token against the ranges on the token ring
   to find the primary owner.
3. **Replication strategy:** It then applies the replication strategy (like
   `NetworkTopologyStrategy`) to identify all other nodes that store a copy of
   that data.

## Dispatch and the snitch

Once the replicas are identified, the coordinator must decide which ones to
contact. It uses a component called the snitch.

**Proximity:** The snitch tells the coordinator which replicas are closest
(e.g., in the same rack or data center).

**Dynamic performance:** A dynamic snitch monitors the performance of all nodes.
If a replica is currently struggling with a heavy compaction or high CPU usage,
the coordinator will prefer a healthier replica to minimize latency.

## Fulfilling consistency

The coordinator does not necessarily wait for every replica to respond. It
follows the consistency level specified by the client:

**Parallel requests:** For a write, the coordinator sends the data to all
replicas simultaneously.

**Blocking for acks:** For a `QUORUM` write, the coordinator waits for a
majority of replicas to acknowledge the write before telling the client
"success."

**Read repair:** During a read, if the coordinator receives different versions
of data from different replicas (based on timestamps), it returns the newest one
to the client and asynchronously updates the out-of-date replicas in the
background.

## Failure handling (hinted handoff)

If the coordinator attempts to route a write to a replica and finds that node is
unresponsive (as determined by the gossip status and the Phi Accrual Failure
Detector), it doesn't necessarily fail the query.

**Hints:** If the consistency level can still be met by other nodes, the
coordinator accepts the write and stores a hint on its local disk.

**Replay:** When gossip indicates the failed node is back online, the
coordinator plays back the hint to bring the node up to date.

## Summary of routing steps

| Phase              | Action                                                          |
|--------------------|-----------------------------------------------------------------|
| **Connection**     | Client picks a node (coordinator) via driver load balancing     |
| **Identification** | Coordinator hashes the key to find replicas using the token map |
| **Optimization**   | Snitch identifies the fastest/closest replicas                  |
| **Execution**      | Coordinator sends requests in parallel                          |
| **Reconciliation** | Coordinator waits for enough acks to satisfy the CL             |

## Related

- [Gossip](gossip.md) - How nodes share cluster state
- [Consistency](consistency.md) - Tunable consistency levels
- [Replication](replication.md) - How replicas are identified

---

Return to [Cassandra](_index.md)
