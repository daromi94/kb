# Data placement

Ceph uses three layers of logical abstraction to partition data: Pools,
Placement Groups, and (for CephFS) dynamic subtree partitioning.

## Pools

At the highest level, a cluster is divided into **Pools**—logical partitions
for isolating different data types or tenants.

**Isolation:** Separate pools for Kubernetes, S3 object store, private cloud.

**Durability rules:** One pool can use 3x replication (for speed), another
erasure coding (for efficiency).

**Quotas:** Limits on space or object count prevent one application from
starving others.

## Placement groups (PGs)

Managing millions of individual objects would overwhelm memory and CPU. Ceph
shards each pool into a configurable number of **Placement Groups**.

**The aggregator:** A PG is a container for a collection of objects. Instead of
tracking "File_A," Ceph tracks "PG_1.0."

**The hashing process:** Object name is hashed, then modulo by PG count:

```text
hash(object_name) % pg_count → PG ID
```

**Dynamic balancing:** Adding OSDs doesn't move individual objects—entire PGs
migrate. This makes rebalancing significantly faster.

## Metadata partitioning (CephFS)

Unique to CephFS, metadata (names, permissions, hierarchy) is managed by
Metadata Servers using **Dynamic Subtree Partitioning**.

**The problem:** A single metadata server becomes a bottleneck as file count
grows.

**The solution:** The directory tree splits into subtrees distributed across
multiple MDS daemons.

**Adaptive:** If `/home/users` becomes extremely busy, Ceph dynamically moves
that subtree to a different MDS without client awareness.

## Layers summary

| Layer      | Unit            | Purpose                                     |
|------------|-----------------|---------------------------------------------|
| Logical    | Pool            | User isolation, storage policy, security    |
| Functional | Placement Group | Data distribution, scalability, rebalancing |
| Metadata   | Subtree         | Scaling file hierarchy across MDS daemons   |

This multi-layered approach lets Ceph handle exabytes of data by replacing
central lookup tables with calculations (CRUSH) and sharded structures (PGs).

## Related

- [CRUSH algorithm](crush-algorithm.md) - How placement is calculated
- [Replication](replication.md) - How data is protected within PGs

---

Return to [Ceph](_index.md)
