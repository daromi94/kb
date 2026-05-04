# Replica types

Replicas in a replication group come in two forms: storage replicas
that hold the full dataset, and log replicas that act as lightweight
quorum participants.

## Storage replicas

A storage replica is the standard member of a replication group. It
maintains both the write-ahead log (WAL) and a B-tree that stores the
actual key-value data. Because it holds the full B-tree, it can serve
read requests. The tradeoff is significant SSD storage and processing
overhead to manage the on-disk index.

## Log replicas

A log replica persists only recent WAL entries — it carries no B-tree
and cannot serve reads. It acts as a Paxos acceptor: votes in the write
quorum to confirm a log entry is durably recorded, but holds no
application state.

Because there is no B-tree to copy, a log replica can join a
replication group in seconds. Bootstrapping a full storage replica
requires copying the B-tree, which takes minutes.

## Availability benefits

When a storage replica becomes unhealthy, the leader immediately adds
a log replica to restore the write quorum. Writes continue to be
acknowledged while the system provisions a replacement storage replica
in the background.

The extra quorum participant also narrows the durability risk window.
If a second failure occurs during repair, more copies of recent WAL
entries exist to recover from.

```text
            Replication group during repair

    AZ-a                AZ-b                AZ-c
+--------------+   +--------------+   +----------------+
| Storage      |   | Storage      |   | Log replica    |
| (leader)     |   | (follower)   |   | (WAL only,     |
| WAL + B-tree |   | WAL + B-tree |   |  added in sec) |
+--------------+   +--------------+   +----------------+
      |                   ^                   ^
      +------------ WAL replicated -----------+
                    quorum: 2 of 3
```

## Related

- [Partitioning and replication](partitioning-and-replication.md) - Replication groups and write path

---

Return to [DynamoDB](_index.md)
