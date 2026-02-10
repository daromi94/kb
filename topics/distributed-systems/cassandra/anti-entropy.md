# Anti-entropy

Anti-entropy is the safety net that ensures distributed data remains
consistent across all replicas, even when writes are missed due to network
partitions or node downtime. Cassandra achieves this through two mechanisms:
read repair (online, during queries) and anti-entropy repair (offline, via
`nodetool repair`).

## Read repair

Read repair is an opportunistic synchronization that happens during normal
query execution.

1. **Trigger:** A client reads data at a consistency level requiring
   multiple replicas (e.g., `QUORUM`).
2. **Detection:** The coordinator receives different versions of the same
   row from different replicas, identified by cell timestamps.
3. **Resolution:** The coordinator returns the most recent version to the
   client and sends a repair write to the lagging replicas.

Read repair is efficient because it only fixes data that is actively being
queried. Data that is never read remains unrepaired until a manual repair
runs.

## Anti-entropy repair

Anti-entropy repair (`nodetool repair`) synchronizes all data across
replicas, including data that has not been read in months. It uses Merkle
trees to identify differences without transferring the full dataset.

## Merkle trees

A Merkle tree (hash tree) provides a compact summary of a large dataset for
efficient comparison.

**Leaves:** Hashes of individual data blocks (rows on disk).

**Branches:** Each parent node is a hash of its children.

**Root:** A single hash representing the state of the entire dataset.

If two nodes have identical data their Merkle tree roots match. If even a
single bit differs, the roots differ and the divergence can be traced down
the branches to the specific leaf. This allows nodes to compare gigabytes of
data by exchanging only a few kilobytes of hashes.

## The repair process

When a manual repair is initiated:

1. **Snapshot and hash:** Each replica performs a validation compaction,
   reading its local data and building a temporary Merkle tree.
2. **Exchange:** Nodes exchange their trees.
3. **Compare:** Starting from the root, nodes walk down divergent branches
   to identify exactly which data ranges differ.
4. **Stream:** Only the differing ranges are streamed from the node with the
   latest data to the out-of-date node.

## Read repair vs anti-entropy repair

| Aspect    | Read repair                        | Anti-entropy repair                      |
|-----------|------------------------------------|------------------------------------------|
| Trigger   | Read query                         | `nodetool repair`                        |
| Scope     | Only the data being read           | All data in the specified range or table |
| Overhead  | Low (piggybacks on normal I/O)     | High (full data scan and hashing)        |
| Mechanism | Timestamp comparison               | Merkle tree comparison                   |
| Use case  | Real-time consistency for hot data | Maintenance and fixing cold data         |

## Why it matters

Without anti-entropy, a node that was offline longer than the hinted handoff
window (typically 3 hours) would permanently hold stale data. These
protocols ensure that every replica eventually converges to the most recent
state.

## Related

- [Hinted handoff](hinted-handoff.md) - Short-term store-and-forward for missed writes
- [Replication](replication.md) - Replica placement and anti-entropy overview
- [Fault tolerance](fault-tolerance.md) - Self-healing mechanisms
- [Tombstones](tombstones.md) - How deletes interact with repair

---

Return to [Cassandra](_index.md)
