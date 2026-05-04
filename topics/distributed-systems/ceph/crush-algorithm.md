# CRUSH algorithm

The **CRUSH** (Controlled Replication Under Scalable Hashing) algorithm is
Ceph's defining technical innovation. It replaces centralized lookup tables
with deterministic calculation, enabling clusters to scale to thousands of
nodes without a metadata bottleneck.

## The problem with lookup tables

Traditional storage systems maintain a central table mapping every object to its
physical location. This creates:

- A single point of failure
- A performance bottleneck (every I/O needs a lookup)
- Memory pressure as the table grows
- Synchronization overhead across nodes

## Calculation over lookup

CRUSH eliminates the table entirely. When a client needs to read or write data:

1. Client provides object ID and pool name
2. Object ID is hashed to a **Placement Group (PG)**
3. PG ID runs through CRUSH with the **Cluster Map**
4. CRUSH outputs exact OSDs where data resides
5. Client connects directly to those OSDs

Because this is a mathematical calculation, the client knows exactly which OSD
to contact without asking a "master" server.

## The CRUSH map

The algorithm uses a hierarchical map of the physical infrastructure:

```text
root default
    rack rack1
        host server1
            osd.0
            osd.1
        host server2
            osd.2
            osd.3
    rack rack2
        host server3
            osd.4
            osd.5
```

## Failure domains

CRUSH rules specify how replicas are distributed across the hierarchy. Setting
the failure domain to `rack` ensures replicas land on different racks:

| Failure domain | Survives               |
|----------------|------------------------|
| `osd`          | Single disk failure    |
| `host`         | Entire server failure  |
| `rack`         | Entire rack power loss |
| `datacenter`   | Site-level disaster    |

## Why this matters

| Traditional approach    | CRUSH approach                 |
|-------------------------|--------------------------------|
| Central lookup table    | Local mathematical function    |
| $O(1)$ lookup + sync    | $O(1)$ calculation, no sync    |
| Memory scales with data | Constant memory (just the map) |
| Single point of failure | Fully distributed              |

The insight: **tables require coordination; math is free and locally
executable**. Replace "where is X?" with "calculate the location of X."

## Related

- [Data placement](data-placement.md) - Pools and Placement Groups
- [Cluster operations](cluster-operations.md) - How maps are distributed

---

Return to [Ceph](_index.md)
