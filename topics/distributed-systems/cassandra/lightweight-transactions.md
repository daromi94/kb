# Lightweight transactions

Standard strong consistency ($W + R > RF$) guarantees reading the most
recent data, but it does not solve the race condition in a read-then-write
sequence. If two clients simultaneously check whether a username exists and
both see it is available, both will write and one will silently overwrite the
other.

Lightweight transactions (LWT) solve this by implementing linearizable
consistency using the Paxos consensus protocol.

## Four-phase Paxos

Standard Paxos uses two phases. Cassandra extends this to four to support
the read-before-write logic required for compare-and-set (CAS) operations
like `INSERT ... IF NOT EXISTS`.

1. **Prepare/Promise:** The coordinator sends a proposal with a unique
   ballot (timestamp) to the replicas. Each replica promises not to accept
   any older proposals.
2. **Read/Results:** The coordinator reads the current state from replicas
   to evaluate the condition (e.g., `IF NOT EXISTS`).
3. **Propose/Accept:** If the condition is met, the coordinator proposes the
   new value. Replicas accept it if they have not promised a newer ballot in
   the meantime.
4. **Commit/Ack:** The coordinator tells replicas to permanently write the
   data and clear the Paxos state.

## Performance cost

An LWT requires multiple round-trips between the coordinator and
replicas, compared to a single round-trip for a standard write.

| Metric      | Standard write              | LWT                             |
|-------------|-----------------------------|---------------------------------|
| Consistency | Eventual or strong          | Linearizable                    |
| Round trips | 1 (coordinator to replicas) | Multiple (Paxos phases)         |
| Throughput  | Very high                   | Significantly lower             |
| Latency     | Low (milliseconds)          | High (multi-phase coordination) |

LWTs are appropriate for low-frequency operations like account creation or
unique constraints. Using them for high-frequency updates (e.g., sensor
heartbeats) creates a bottleneck.

## Single-partition scope

Cassandra LWTs are strictly single-partition. Paxos state (the current
ballot and promise) is stored as hidden metadata within the partition
itself. This means a transaction on one partition never blocks or interferes
with a transaction on another, allowing linear scalability as long as
transactions hit different partitions.

## Paxos vs two-phase commit

Traditional distributed transactions often use two-phase commit (2PC), which
is blocking: if the coordinator fails mid-process, resources can remain
locked indefinitely. Paxos is consensus-based: as long as a quorum of
replicas is alive, the transaction can be resolved or timed out without
locking the table.

## Related

- [Consistency](consistency.md) - Tunable consistency levels and strong consistency formula
- [Replication](replication.md) - Quorum-based replica acknowledgment

---

Return to [Cassandra](_index.md)
