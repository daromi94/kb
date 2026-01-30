# HBase consistency model

HBase is a CP system (Consistent and Partition Tolerant), enforcing strong
consistency at the expense of availability during failures.

## Single-owner model

HBase guarantees that every read returns the most recent write through strict
single ownership:

- **One region, one server:** At any moment, a specific region is served by
  exactly one RegionServer
- **Atomic row operations:** Since only one server handles a row key, writes
  are atomic without distributed coordination
- **No stale reads:** Reads always go to the single source of truth, never to
  backup replicas

This eliminates the need for conflict resolution strategies like last-write-wins
or vector clocks.

## Partition tolerance via HDFS

HBase separates computing (RegionServers) from storage (HDFS). Even if a
RegionServer is partitioned from the network, data remains safely replicated 3x
across HDFS DataNodes.

## Availability trade-off

To maintain single-owner consistency, HBase sacrifices availability during
failures.

**Split-brain prevention sequence:**

```
1. RegionServer loses contact
         |
         v
2. ZooKeeper session expires
         |
         v
3. HMaster marks server dead
         |
         v
4. Regions become UNAVAILABLE  <-- Availability loss
         |
         v
5. Master reassigns to new server
         |
         v
6. New server replays WAL from HDFS
         |
         v
7. Service restored
```

During the recovery window (seconds to minutes), requests to affected regions
fail. The system refuses to answer rather than risk returning stale data or
allowing concurrent modifications.

## Philosophy comparison

| Aspect           | HBase (CP)                       | Cassandra (AP)               |
|------------------|----------------------------------|------------------------------|
| Write handling   | Only region owner accepts writes | Any node can accept writes   |
| During partition | Writes to affected regions fail  | Writes go to available nodes |
| Recovery         | Wait for region reassignment     | Hinted handoff repairs later |
| Philosophy       | "Better to be down than wrong"   | "Better to be up and wrong"  |

## Implications

- Expect brief unavailability during server failures
- Plan for RegionServer failures in application error handling
- Master failover also causes temporary unavailability until standby activates
- Trade-off is worthwhile when data correctness is more important than uptime

## Related

- [Architecture](architecture.md) - How master/slave enables this model
