# Partitioning and replication

A DynamoDB table is split into partitions and each partition is
replicated across availability zones for durability and availability.

## Partitions

A table is decomposed into physical units called partitions. Each
partition owns a disjoint, contiguous slice of the table's key range.
The partition key's hash value determines which partition holds a given
item, letting the request router contact the correct node directly.

Partitions are the unit of both storage and throughput allocation.
Splitting and moving partitions is how DynamoDB scales a table's
capacity without downtime.

## Replication groups

Each partition is stored as a replication group — a set of replicas
spread across multiple availability zones. If an entire AZ or a single
node fails, the remaining replicas continue to serve traffic.

```
       Replication group (one partition)

    AZ-a            AZ-b            AZ-c
+----------+   +------------+   +------------+
| Replica  |   | Replica    |   | Replica    |
| (leader) |   | (follower) |   | (follower) |
+----------+   +------------+   +------------+
      |               ^               ^
      +----- writes replicated -------+
```

## Leader election with Multi-Paxos

Each replication group uses Multi-Paxos for leader election and write
consensus. Any replica can trigger an election when it detects the
current leader is unhealthy. The elected leader holds a leadership
lease that it must periodically renew to stay in the role.

**Leader responsibilities:**

- Serve all write requests
- Serve strongly consistent read requests
- Replicate writes to followers

Eventually consistent reads can be served by any replica.

## Leader failover

When a peer replica detects the leader is unresponsive, it proposes a
new election. The newly elected leader waits for the previous leader's
lease to expire before serving traffic, preventing two nodes from
acting as leader simultaneously.

## Related

- [Data model](data-model.md) - Partition key hashing and item
  placement
- [Performance](performance.md) - Request routing and admission
  control

---

Return to [DynamoDB](_index.md)
