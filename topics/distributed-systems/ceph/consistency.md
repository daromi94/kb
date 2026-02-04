# Consistency Model

In the CAP theorem (Consistency, Availability, Partition Tolerance), Ceph is
fundamentally a **CP system**. It prioritizes Consistency and Partition
Tolerance over absolute Availability.

## CAP Mapping

### Consistency (C) - Strong

When a write occurs, the client receives no acknowledgment until data has been
replicated across the required number of OSDs. A subsequent read always returns
the most recently written version.

### Partition Tolerance (P) - High

Ceph uses a quorum-based system for Monitors. If a network split occurs, only
the partition containing a majority of Monitors can continue operating. This
prevents split-brain scenarios where different parts accept conflicting writes.

### Availability (A) - Partial

This is the trade-off. During significant failures or partitions that break
quorum, Ceph becomes unavailable for I/O. It would rather fail requests than
provide inconsistent data.

## The Peering State

The CP nature is most visible during failures. When an OSD goes down, affected
Placement Groups enter a **Peering** state:

- All I/O to those PGs is **blocked**
- Remaining OSDs must agree on current data state before allowing new I/O
- Technically reduces availability for a few seconds
- Guarantees consistency is never compromised

## RGW: The AP Exception

While core RADOS is strictly CP, the RADOS Gateway can behave more like an
**AP system** in specific configurations:

**Multisite replication:** When syncing across geographic regions, replication
is often asynchronous. A write to Region A may be acknowledged before reaching
Region B.

If the inter-region link breaks, both sites stay available but may serve
inconsistent data temporarily.

## Summary

| Attribute           | Status      | Mechanism                                   |
|---------------------|-------------|---------------------------------------------|
| Consistency         | **Strong**  | Synchronous replication, Primary model      |
| Availability        | **Partial** | Sacrificed during partitions/quorum loss    |
| Partition Tolerance | **High**    | Monitor quorum (Paxos) prevents split-brain |

## Related

- [Read/write paths](read-write-paths.md) - How consistency is enforced
- [Replication](replication.md) - The synchronous replication model
- [Cluster operations](cluster-operations.md) - How failures are detected

---

Return to [Ceph](_index.md)
