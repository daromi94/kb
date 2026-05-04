# Cluster operations

A Ceph cluster functions as a distributed, autonomous entity where intelligence
is decentralized. Every component—including clients—can calculate data
locations independently.

## The cluster map

The cluster's coordination begins with **Monitors** maintaining the Cluster Map:

| Sub-map     | Contents                              |
|-------------|---------------------------------------|
| OSD map     | Which disks are up/down and in/out    |
| Monitor map | Which monitors are in quorum          |
| CRUSH map   | Physical hierarchy of the data center |
| PG map      | Placement group states                |
| MDS map     | Metadata server ranks and state       |
| Manager map | Active and standby manager daemons    |

To perform any action, a client first contacts a Monitor to get the latest map.
Once obtained, the client no longer needs the Monitor for data I/O.

## Versioned state (epochs)

Cluster state is versioned by **Epochs**. Every message carries a version
number.

Instead of perfect real-time synchronization, nodes "catch up" lazily. If OSD A
notices OSD B has an older map epoch, A gossips the incremental updates to B.
This lazy distribution keeps the cluster in sync without global broadcasts.

## Self-healing

The cluster repairs itself without human intervention through continuous
monitoring:

**Heartbeating:** OSDs constantly "gossip" with neighbors. If OSD 12 stops
responding, OSD 5 and OSD 22 report it to Monitors.

**Map update:** Monitors mark OSD 12 as "down" and "out," broadcast a new map.

**Rebalancing:** Every OSD receives the new map, re-runs CRUSH, and realizes
data from OSD 12 now belongs elsewhere. OSDs migrate data among themselves to
restore replica count.

## Data ingestion flow

1. **Discovery:** Client gets Cluster Map from Monitor
2. **Calculation:** Client runs CRUSH to identify OSDs
3. **I/O:** Client writes directly to Primary OSD
4. **Safety:** Primary replicates to Secondary OSDs
5. **Maintenance:** Cluster detects failures and rebalances

## The manager role

While Monitors handle cluster "state," the **Manager** handles "status":

- Collects performance metrics (I/O, disk usage)
- Provides data to Prometheus or Ceph Dashboard
- Runs the `balancer` module to fine-tune data distribution

## Related

- [Read and write paths](read-write-paths.md) - Detailed I/O flow
- [CRUSH algorithm](crush-algorithm.md) - How locations are calculated
- [Consistency model](consistency.md) - What happens during failures

---

Return to [Ceph](_index.md)
