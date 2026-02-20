# Transactions

DynamoDB provides ACID transactions for operations that must update
multiple items as a single indivisible unit. A transaction can span
up to 100 items or 4 MB of data, and items may reside on different
partitions.

## ACID guarantees

| Property    | Guarantee                                              |
|-------------|--------------------------------------------------------|
| Atomicity   | All operations succeed or all fail — no partial writes |
| Consistency | Data remains in a valid state after every transaction  |
| Isolation   | Serializable — uncommitted changes are invisible       |
| Durability  | Committed changes survive subsequent failures          |

## Two-phase commit

Transactions use a two-phase commit protocol to coordinate writes
across partitions:

1. **Prepare:** The transaction coordinator contacts each partition
   involved and asks it to validate and lock the affected items.
2. **Commit:** Once all partitions acknowledge readiness, the
   coordinator issues a commit. If any partition rejects, the entire
   transaction rolls back.

Request Routers forward transaction requests to dedicated transaction
coordinators that manage this process. The underlying Multi-Paxos
replication ensures a transaction can complete as long as a quorum
of replicas is available for each affected item.

## Performance

Transactions carry overhead from the two-phase protocol and are
roughly 3-4x slower than equivalent batch operations. Latencies
remain sub-20ms but are notably higher than single-item reads and
writes. The system is designed so that this overhead does not
cascade into delays for non-transactional operations on the same
table.

## Related

- [Performance](performance.md) - Request routing and admission
  control mechanisms
- [Operational lessons](operational-lessons.md) - TLA+ verification
  of distributed protocols

---

Return to [DynamoDB](_index.md)
