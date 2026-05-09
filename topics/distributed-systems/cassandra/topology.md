# Topology

Topology in Cassandra is the logical and physical arrangement of the
cluster. The hierarchy moves from the smallest unit (node) to the largest
(cluster), and Cassandra uses this structure to distribute replicas for
both performance and disaster recovery.

## Hierarchy

| Level       | Maps to                            | Purpose                                     |
|-------------|------------------------------------|---------------------------------------------|
| Node        | Server or VM                       | Stores a portion of data; handles requests  |
| Rack        | Server rack or availability zone   | Isolates against localized hardware failure |
| Data center | Geographic region or virtual group | Isolates against regional outages/workloads |
| Cluster     | The entire ring                    | Global data ownership and scalability       |

## Nodes

A node is a single Cassandra instance. Each node owns one or more token
ranges on the hash ring, stores the corresponding data, and handles
read/write requests. Because Cassandra is peer-to-peer, no node is more
important than another — any node can act as coordinator for a query.

## Racks

A rack is a logical grouping of nodes within a data center, typically
mapping to a physical server rack or a cloud availability zone. Cassandra
is rack-aware: when placing replicas, it distributes them across different
racks so that a top-of-rack switch failure or power outage does not take
down all copies of a partition.

## Data centers

A data center is a logical grouping of racks. Common uses:

**Geographic redundancy:** Replicate data across continents. If an entire
DC loses connectivity, traffic routes to the surviving DC.

**Workload isolation:** Designate one DC for real-time traffic (OLTP) and
another for analytics or Spark jobs. Cross-DC replication is asynchronous,
so the analytical workload does not affect production latency.

## The snitch

The snitch tells Cassandra how nodes map to racks and data centers.
Replication strategies and the coordinator's routing decisions depend on
this mapping.

| Snitch                      | Use case                                            |
|-----------------------------|-----------------------------------------------------|
| GossipingPropertyFileSnitch | Production standard; local config shared via gossip |
| Ec2Snitch / Ec2MultiRegion  | Maps AWS regions and AZs to DCs and racks           |
| SimpleSnitch                | Development only; single DC and rack                |

---

Return to [Cassandra](_index.md)
