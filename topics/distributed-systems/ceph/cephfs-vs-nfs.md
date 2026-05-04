# CephFS vs NFS

Comparing CephFS and NFS involves evaluating a distributed, software-defined
storage cluster against a traditional client-server protocol. Both provide
shared file systems but differ significantly in architecture and use cases.

## Architectural comparison

| Feature     | NFS                    | CephFS                            |
|-------------|------------------------|-----------------------------------|
| Model       | Client-server          | Distributed cluster               |
| Scalability | Vertical (scale-up)    | Horizontal (scale-out)            |
| Metadata    | Single server          | Cluster of MDS daemons            |
| Data path   | Client → Server → Disk | Client → OSD cluster (direct I/O) |
| Redundancy  | RAID on server or HA   | Replication or erasure coding     |

## Key differences

### Scalability and bottlenecks

**NFS:** Performance limited by single server's CPU, RAM, and network. More
clients create bottlenecks for both data throughput and metadata operations.

**CephFS:** Designed for petabyte scale. Add nodes for more performance/capacity.
Data striped across OSDs, metadata distributed across multiple active MDS.

### Data path

**NFS:** Every request goes through the NFS server. Simple but creates
congestion. For small workloads, often has lower latency due to less overhead.

**CephFS:** Once a client gets metadata, it communicates directly with OSDs.
Enables massive parallel throughput but may have higher latency for small-file
operations due to distributed consistency overhead.

### Availability

**NFS:** Single point of failure by default. HA requires external tools
(Heartbeat, Pacemaker, DRBD) for failover.

**CephFS:** HA built-in. Disk or node failure triggers automatic re-replication.
File system stays accessible as long as cluster maintains quorum.

## Complexity

**NFS:** Easy setup. Native OS support. Minimal resources required.

**CephFS:** High management overhead. Requires dedicated server cluster, robust
network (10GbE minimum), distributed systems expertise.

## When to use which

### Use NFS if:

- Simple setup with few clients
- Low-latency access to relatively small data
- Limited hardware or expertise for cluster management
- Legacy applications needing simple POSIX without high throughput

### Use CephFS if:

- Capacity and performance must scale linearly with data growth
- Self-healing system required to survive hardware failures
- Large-scale environment (OpenStack, Kubernetes, HPC)
- Unified storage platform also providing Block and Object storage

## The trade-off

**Simplicity vs Scalability.** NFS for ease of use and low latency at small
scale. CephFS for resilience and massive throughput at large scale.

## Related

- [Storage interfaces](storage-interfaces.md) - CephFS among Ceph's interfaces
- [RADOS architecture](rados.md) - The foundation CephFS builds on

---

Return to [Ceph](_index.md)
