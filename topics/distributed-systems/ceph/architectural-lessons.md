# Architectural lessons

Design patterns and insights from Ceph's architecture applicable to distributed
systems broadly.

## 1. Intelligence at the Edge (Smart Clients)

Traditional systems use a central gateway to route every request—a hard
bottleneck.

**The Ceph approach:** Give clients the CRUSH algorithm so they calculate data
locations independently.

**Takeaway:** If every node can "calculate" truth instead of "asking" for it,
you scale to thousands of nodes without a centralized master.

## 2. Decoupling Data and Control Planes

In CephFS, file contents (data) and file names/permissions (metadata) live in
separate systems.

- **Data Plane (RADOS):** File bytes stored as objects on OSDs
- **Control Plane (MDS):** Separate servers manage directory hierarchy

**Takeaway:** Decouple data path from control path. Scale metadata performance
(more MDS) and storage capacity (more OSDs) independently.

## 3. Calculation Over Lookup

Most systems find data via database lookup—$O(1)$ or $O(\log n)$ but requires
memory and synchronization.

**The Ceph approach:** Deterministic mapping via CRUSH replaces stateful tables.

**Takeaway:** Tables require coordination; math is free and locally executable.
Replace "where is X?" with "calculate the location of X."

## 4. Autonomic Self-Healing

Ceph doesn't wait for administrators. OSDs monitor each other through
heartbeating and trigger rebalancing automatically.

**Takeaway:** Build peering and self-correction into the lowest software levels.
A distributed system is only as strong as its ability to survive partial failure
without human intervention.

## 5. CAP Realism

Ceph is a CP system. It blocks I/O rather than risk split-brain where nodes
disagree on data.

**Takeaway:** You cannot have it all. In storage, Consistency is usually
non-negotiable. Make the trade-off explicit.

**CephFS Caps:** Manages consistency across clients using Distributed
Capabilities—centralized authority delegates "leases" for safe caching while
retaining revocation rights.

## 6. Dynamic Subtree Partitioning

Standard hashing balances load but destroys locality (keeping a folder's files
together).

**The CephFS approach:** Monitor directory "heat." If `/home/users` gets busy,
dynamically migrate that subtree to a less busy MDS.

**Takeaway:** Preserving metadata locality while providing horizontal
scalability is the "Holy Grail" of distributed file systems.

## 7. Versioned State (Epochs)

Cluster state is versioned. Every message carries a version number.

**The approach:** Instead of perfect real-time sync, let nodes catch up lazily.
OSD A notices OSD B has older epoch, gossips incremental updates.

**Takeaway:** Lazy distribution keeps clusters in sync without global broadcasts
for every minor event.

## Summary

| Challenge    | Traditional         | Ceph Lesson                  |
|--------------|---------------------|------------------------------|
| Finding Data | Global lookup table | Local math (CRUSH)           |
| Scaling      | Vertical            | Horizontal                   |
| Hotspots     | Static hashing      | Dynamic subtree partitioning |
| Failures     | Admin intervention  | Autonomic recovery           |
| State Sync   | Global broadcast    | Lazy epoch-based gossip      |

## Related

- [CRUSH algorithm](crush-algorithm.md) - Calculation over lookup in detail
- [Cluster operations](cluster-operations.md) - Self-healing and epochs
- [Consistency](consistency.md) - The CP trade-off

---

Return to [Ceph](_index.md)
