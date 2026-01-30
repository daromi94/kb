# HBase overview

Apache HBase is an open-source, distributed, column-oriented NoSQL database
built on top of HDFS. It is modeled after Google's Bigtable paper and provides
random, real-time read/write access to billions of rows and millions of columns.

## Core concept

HBase is a **distributed, sorted, multidimensional map**. Unlike relational
databases which are row-oriented and schema-rigid, HBase is column-family
oriented and schema-flexible. It is written in Java and integrates natively
with the Hadoop ecosystem.

## CAP theorem position

HBase is a **CP system** (Consistent and Partition Tolerant), prioritizing
strong consistency over availability. This contrasts with Cassandra's AP
approach with tunable eventual consistency.

## When to use HBase

**Good fit:**

- Strong consistency requirements
- Massive datasets (petabytes)
- Tight integration with Hadoop/Spark for batch processing
- Range scans over sorted data
- Text search backends

**Poor fit:**

- Simple setup requirements (HBase has many moving parts)
- Cannot tolerate occasional downtime during Master failover
- High-write, always-on applications (consider Cassandra instead)

## HBase vs Cassandra

| Feature      | HBase                               | Cassandra                         |
|--------------|-------------------------------------|-----------------------------------|
| Architecture | Master-Slave (HMaster/RegionServer) | Peer-to-Peer (Leaderless)         |
| CAP theorem  | CP (Consistency, Partition)         | AP (Availability, Partition)      |
| Consistency  | Strong (atomic single-row ops)      | Tunable (eventual to strong)      |
| Best for     | Scans, batch processing             | High-write, always-on (IoT, chat) |
| Internals    | Relies on HDFS & ZooKeeper          | Manages own storage & gossip      |

## Related

- [Architecture](architecture.md) - How master/slave coordination works
- [Consistency model](consistency-model.md) - Why HBase chooses CP
