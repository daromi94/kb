# Overview

Apache Cassandra is a distributed NoSQL database that scales horizontally
across commodity servers. Born at Facebook and later open-sourced as an
Apache project, it combines the distribution design of Amazon's Dynamo
with the data model of Google's Bigtable.

## Core architecture principles

### Masterless (peer-to-peer) design

Unlike traditional databases that use a leader/follower setup, Cassandra is
masterless. Every node in the cluster is identical and can handle any read or
write request. This eliminates single points of failure. If one node goes down,
the cluster continues to operate without needing an expensive election process.

### Linear scalability

Cassandra scales horizontally. If a cluster of 10 nodes can handle 100,000
transactions per second, adding 10 more nodes will reliably double that capacity
to 200,000. Add nodes to the ring without taking the system offline.

### High availability and fault tolerance

Data is automatically replicated across multiple nodes. You can configure
replication across different data centers or availability zones. If a rack fails
or a data center loses power, Cassandra serves the data from another replica
seamlessly.

## The ring

Nodes in Cassandra are logically organized in a ring. Data is distributed across
these nodes using consistent hashing.

**Partitioning:** Every piece of data has a partition key. Cassandra hashes this
key to a value that falls into a specific range owned by a node.

**Gossip protocol:** Nodes constantly communicate using a peer-to-peer protocol
called Gossip to share state information about the health and location of other
nodes in the cluster.

## Performance characteristics

| Feature              | Detail                                                      |
|----------------------|-------------------------------------------------------------|
| **Write throughput** | Extremely fast via LSM-trees (sequential disk I/O)          |
| **Read latency**     | Optimized via Bloom filters and caching; slower than writes |
| **Consistency**      | Tunable per-query from eventual to strong                   |

## When to use Cassandra

Cassandra excels in specific scenarios:

- **IoT and telemetry:** High-velocity writes from millions of sensors
- **Time-series data:** Logs or metrics indexed by time
- **User profiles:** Scaling to hundreds of millions of users
- **Fraud detection:** Real-time analysis of transactions at scale

**When to avoid:** Complex ACID transactions across multiple tables, heavy ad-hoc
joins, or datasets small enough for a single relational server.

---

Return to [Cassandra](_index.md)
