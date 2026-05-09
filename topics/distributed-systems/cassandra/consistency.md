# Consistency

In Cassandra, consistency refers to how up-to-date and synchronized rows of data
are across all their replicas. Unlike traditional relational databases that
enforce strict ACID compliance, Cassandra offers tunable consistency. This
allows you to choose the trade-off between high availability (speed) and data
accuracy on a per-query basis.

## Consistency levels (CL)

The consistency level is a setting provided by the client (driver) for every
read or write operation. It determines how many replicas must acknowledge the
request before the coordinator considers the operation successful.

### Write consistency levels

- **ANY:** The write must be stored on at least one node (even if it's just a
  hint on the coordinator). Highest availability but lowest durability.
- **ONE / TWO / THREE:** The write must be acknowledged by at least $X$ replica
  nodes.
- **QUORUM:** The write must be acknowledged by a majority of replicas:
  $\lfloor (RF / 2) + 1 \rfloor$.
- **ALL:** The write must be acknowledged by every replica. If one node is down,
  the write fails.

### Read consistency levels

- **ONE:** The coordinator returns data from the first replica to respond.
  Fastest read.
- **QUORUM:** The coordinator queries a majority of replicas and returns the
  data with the most recent timestamp.
- **ALL:** The coordinator queries all replicas. Highest consistency, but fails
  if any node is unreachable.

## The formula for strong consistency

Cassandra is eventually consistent by default, but you can achieve immediate
consistency (where a read is guaranteed to see the latest write) by balancing
your read ($R$) and write ($W$) levels against your replication factor ($RF$).

The rule for strong consistency is:

$$W + R > RF$$

**Example with $RF=3$:**

If you write at QUORUM ($W=2$) and read at QUORUM ($R=2$):

$$2 + 2 > 3$$

Because you are interacting with a majority in both cases, there is a
mathematical guarantee that the read quorum and the write quorum will overlap by
at least one node. That overlapping node ensures the reader sees the latest
version.

## Tunable consistency trade-offs

The choice of consistency level directly impacts the CAP theorem (consistency,
availability, partition tolerance).

| Strategy               | Consistency level            | Latency | Availability |
|------------------------|------------------------------|---------|--------------|
| **High throughput**    | Write: ONE / Read: ONE       | Lowest  | Highest      |
| **Strong consistency** | Write: QUORUM / Read: QUORUM | Medium  | Medium       |
| **Maximum safety**     | Write: ALL / Read: ALL       | Highest | Lowest       |

## Eventual consistency and self-healing

If you choose lower consistency levels (like `ONE`), replicas may temporarily
hold different versions of the data. Cassandra uses entropy reduction mechanisms
to eventually synchronize them:

**Read repair:** If a coordinator performs a read and notices that one replica
has an older timestamp than the others, it sends a background update to the
out-of-sync node.

**Hinted handoff:** If a write is sent to a node that is down, the coordinator
stores a hint. When the node comes back online, the coordinator replays the
missed write.

**Anti-entropy (manual repair):** Using `nodetool repair`, Cassandra compares
Merkle trees (hash trees) across nodes to find and fix inconsistencies in the
background.

## Lightweight transactions (LWT)

For operations that require linearizable consistency (e.g., "create user if not
exists"), Cassandra uses the Paxos consensus protocol. This involves a
multi-phase prepare/propose/commit cycle. It ensures that a specific condition
is met across the cluster before the write is finalized, though it carries a
significant performance penalty compared to standard writes.

---

Return to [Cassandra](_index.md)
