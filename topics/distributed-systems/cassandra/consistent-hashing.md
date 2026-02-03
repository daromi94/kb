# Consistent hashing

Consistent hashing is a fundamental technique used in distributed systems to
partition data across a cluster of nodes. It addresses two primary weaknesses of
traditional modulo hashing: massive data migration when the number of nodes ($N$)
changes, and the risk of uneven load distribution.

## The hash ring

In consistent hashing, the output range of a hash function (e.g., $0$ to
$2^{64}-1$) is treated as a fixed circular space, often called a hash ring.

**Node placement:** Each node in the cluster is hashed based on its identifier
(like an IP address or hostname) and placed at a specific point on this ring.

**Data placement:** When data needs to be stored, its partition key is hashed to
find its position on the same ring.

**The clockwise rule:** To find which node owns the data, you start at the
data's hash position and travel clockwise around the ring. The first node you
encounter is the one responsible for storing that data.

## Handling cluster changes

The "consistency" in consistent hashing refers to how little data moves when the
cluster configuration changes.

**Adding a node:** When a new node is added to the ring, it only captures data
from the node immediately following it in a counter-clockwise direction. Only a
small fraction of the total keys ($1/N$) need to be re-mapped.

**Removing a node:** If a node fails or is removed, its keys simply fall to the
next node clockwise. Only the data on the departing node is affected; the rest
of the cluster remains untouched.

## Virtual nodes (vnodes)

A basic consistent hashing ring can suffer from hot spots if nodes are spaced
unevenly or if some keys are accessed more frequently. Modern systems like
Cassandra use virtual nodes to address this.

Instead of a physical node appearing only once on the ring, it is hashed
multiple times with different seeds, placing dozens or hundreds of virtual nodes
across the ring.

**Uniformity:** Spreading many virtual segments across the ring makes it
statistically much more likely that data will be distributed evenly.

**Heterogeneity:** You can assign more virtual nodes to powerful servers and
fewer to smaller ones, balancing load based on hardware capacity.

**Speedy recovery:** If a physical node fails, its many virtual segments are
scattered. Consequently, its load is distributed among many different neighbors
rather than just one, preventing a cascading failure where one neighbor gets
overwhelmed.

## Comparison

| Feature           | Traditional hashing                     | Consistent hashing            |
|-------------------|-----------------------------------------|-------------------------------|
| **Node addition** | Almost all keys move (total disruption) | Only $1/N$ keys move          |
| **Node removal**  | Almost all keys move                    | Only keys from that node move |
| **Scalability**   | Hard to scale dynamically               | Designed for elastic scaling  |
| **Load balance**  | Hard to tune                            | Tunable via virtual nodes     |

## Related

- [Partitioning](partitioning.md) - How Cassandra applies consistent hashing
- [Replication](replication.md) - How data is copied after placement
- [Fault tolerance](fault-tolerance.md) - How vnodes aid recovery

---

Return to [Cassandra](_index.md)
