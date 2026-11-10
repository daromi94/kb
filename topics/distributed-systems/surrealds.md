# SurrealDS

SurrealDS is a distributed transactional storage engine built around a central architectural decision:

**Separate the durability and ownership of data from the compute nodes that execute queries, without placing remote object storage on the critical path of every transaction.**

It combines several established distributed systems techniques:

- Shared, durable object storage for persistent database pages.
- Locally replicated commit logs for low-latency transactional writes.
- A sequencer for deterministic transaction ordering.
- Local caches and snapshot-aware reads.
- Copy-on-write, content-addressed storage structures.
- Coordinated failover with correctness checks.

The interesting part is not any individual technique. It is how these mechanisms interact to provide fault tolerance while avoiding full database replication on every compute node.

## 1. The architectural problem

Consider a conventional distributed database where compute and storage are coupled.

```text
                 Clients
                    |
                    v
              Load Balancer
                    |
    +---------------+---------------+
    |               |               |
 Node A          Node B          Node C
    |               |               |
 Disk A          Disk B          Disk C
    |               |               |
    +---------------+---------------+
               Replication

Each node may hold a full database copy.
```

This architecture has desirable properties. Data can be read locally, replicas can survive failures, and replication can provide strong consistency.

However, it creates several problems.

**Compute and storage scaling become coupled.**

Suppose the dataset is 10 TB, replicated three times.

Adding another full replica to increase query capacity potentially means provisioning another 10 TB of storage, even if the workload only needs additional CPU.

**Recovery becomes proportional to the dataset.**

A replacement replica may need substantial data synchronization before it is fully operational. This can generate network traffic and compete with normal database operations.

**Compute nodes become expensive to replace.**

Their local disks contain significant persistent state. Adding and removing nodes requires careful data movement.

The underlying problem is that a database node is simultaneously responsible for executing queries, storing data, and maintaining durability.

The architectural question becomes:

**Can compute nodes be relatively disposable while the database remains durable, transactional, and highly available?**

## 2. Overall SurrealDS architecture

SurrealDS answers this question with three storage tiers and distinct replication responsibilities.

```text
                          Clients
                             |
                             v
                       Load Balancer
                             |
       +---------------------+---------------------+
       |                     |                     |
     AZ A                  AZ B                  AZ C
       |                     |                     |
+------------+        +------------+        +------------+
|   Node A   |        |   Node B   |        |   Node C   |
| Sequencer  |        |  Witness   |        |  Listener  |
+------------+        +------------+        +------------+
|   Query    |        |   Query    |        |   Query    |
|   Engine   |        |   Engine   |        |   Engine   |
+------------+        +------------+        +------------+
|   Memory   |        |   Memory   |        |   Memory   |
|   Cache    |        |   Cache    |        |   Cache    |
+------------+        +------------+        +------------+
|   Local    |        |   Local    |        |   Local    |
|    Log     |        |    Log     |        |    Log     |
| Disk Cache |        | Disk Cache |        | Disk Cache |
+------------+        +------------+        +------------+
       |                     |                     |
       +---------------------+---------------------+
                             |
                             v
                    Shared Object Store
                             |
                             v
                 +----------------------+
                 | Database Manifest    |
                 | Immutable Tree Pages |
                 | Persisted Log Data   |
                 +----------------------+
```

Every node runs a complete query engine, but the nodes have different responsibilities in the transaction protocol.

| Component              | Responsibility                                                             |
| ---------------------- | -------------------------------------------------------------------------- |
| Sequencer              | Assigns transaction order and coordinates commits                          |
| Acking witness         | Maintains a second durable log copy in another failure domain              |
| Listener               | Follows committed changes, serves queries, and can participate in recovery |
| Memory and disk caches | Keep frequently accessed data close to compute                             |
| Object storage         | Holds persistent database pages and published database state               |

Nodes communicate over QUIC with mutual TLS. The object store is shared across the group, while the transactional commit path uses local disks and inter-node replication.

This creates an important distinction:

**The database has shared durable storage, but it does not perform every transaction directly against that shared storage.**

That's the foundation for understanding the rest of the design.

## 3. Write path: replicate the commit log, not the entire database

**The most important design decision is that a transaction becomes durable before its changes are materialized into object storage.**

Consider a transaction updating account A.

```text
Client            Node C              Sequencer              Witness
   |                 |                    |                     |
   |---- UPDATE ---->|                    |                     |
   |                 |                    |                     |
   |                 |----- COMMIT ------>|                     |
   |                 |                    |                     |
   |                 |                Validate                  |
   |                 |                and order                 |
   |                 |                    |                     |
   |                 |               Append log                 |
   |                 |               Flush disk                 |
   |                 |                    |                     |
   |                 |                    |---- Replicate ----->|
   |                 |                    |                     |
   |                 |                    |                Append log
   |                 |                    |                Flush disk
   |                 |                    |                     |
   |                 |                    |<------- ACK --------|
   |                 |                    |                     |
   |                 |<----- COMMIT ------|                     |
   |<--- SUCCESS ----|                    |                     |
   |                 |                    |                     |

 Background work
        |
        v
 Upload log data
        |
        v
Build tree pages
        |
        v
Publish manifest
        |
        v
  Object Store
```

The significant detail is that the object-store operations occur after the transaction has been acknowledged.

### Why use a sequencer?

Distributed systems need an unambiguous answer to a fundamental question:

If two transactions execute concurrently, which transaction logically happened first?

Suppose two nodes receive conflicting updates:

```text
Node A: SET x = 10

Node B: SET x = 20
```

Without an ordering or conflict-resolution mechanism, different replicas could apply these transactions in different orders.

SurrealDS designates one sequencer per group.

```text
    Concurrent Transactions
               |
 +-------------+-------------+
 |                           |
T1                          T2
 |                           |
 +-------------+-------------+
               |
               v
           Sequencer
               |
               v
      Ordered Commit Log
               |
   +-----------+-----------+
   |                       |
Seq 100                 Seq 101
  T1                      T2
```

The ordering establishes a common transaction history. Conflict detection determines whether a transaction is allowed to commit against that history; **assigning a sequence position is not, by itself, sufficient for isolation.**

This separates two responsibilities:

**Transaction execution is distributed across nodes.**

**Commit ordering is centralized within the group.**

That is an intentional compromise. It simplifies reasoning about transaction order and recovery, but introduces a serialized component into the write path.

### Why replicate the log instead of writing directly to object storage?

Consider two approaches.

**Approach A: synchronous remote storage**

```text
     Transaction
          |
          v
Remote object storage
          |
          v
Durability confirmed
          |
          v
     Acknowledge
```

Every transaction depends on remote storage latency.

**Approach B: replicated local logging**

```text
          Transaction
               |
               v
       Local durable log
               |
               +--------> Remote zone durable log
               |                      |
               |<---------------------+
               |
               v
          Acknowledge
               |
               v
Async object-store persistence
```

The second approach replaces synchronous object-storage operations with local disk flushes and a cross-zone replication exchange.

It does not eliminate durability costs. A commit still depends on disk synchronization, network communication, and the second node's durable acknowledgment.

However, it removes object-storage writes, object creation, and tree publication from the immediate commit path.

The general pattern is:

**Use a low-latency write-optimized representation for recent mutations, and asynchronously transform it into a storage-optimized representation.**

This is a common principle behind write-ahead logging, LSM-based storage, and log-based replication.

## 4. Read path: merge immutable pages with recent mutations

The write architecture creates an interesting problem.

Suppose the object store contains data through transaction sequence 100.

Three additional transactions have committed:

```text
Object Store
  Database state through sequence 100

Local Commit Log
  101: account:A = 50
  102: account:B = 75
  103: account:A = 60
```

A query for `account:A` must return the value appropriate to its snapshot.

It cannot simply read the object store, because the object-store pages have not yet incorporated transaction 103.

SurrealDS uses a combination of the persisted tree and newer logged changes.

```text
                      SELECT account:A
                              |
                              v
                        Query Engine
                              |
                              v
                       Pinned Snapshot
                              |
        +---------------------+---------------------+
        |                                           |
        v                                           v
Recent Log Index                             Persistent Tree
        |                                           |
  Changes newer                               Memory Cache
 than watermark                                     |
        |                                           |
        |                                      Disk Cache
        |                                           |
        |                                     Object Store
        |                                           |
        +---------------------+---------------------+
                              |
                              v
                       Resolve visible
                         key version
                              |
                              v
                           Result
```

A watermark identifies the log position already incorporated into the persistent tree.

For a snapshot at sequence 103, the read combines the tree at watermark 100 with the relevant changes from sequences 101 through 103. The actual lookup is optimized by indexes and caches; it does not require scanning the entire commit log on every read.

### Why is this design useful?

It gives the system two complementary representations of database state.

The commit log is optimized for:

- Sequential appends.
- Replication.
- Transaction ordering.
- Recovery of recent mutations.

The persistent tree is optimized for:

- Key and range lookups.
- Long-term storage.
- Sharing unchanged pages.
- Loading data on demand.

This distinction avoids forcing one data structure to optimize simultaneously for every workload.

### Why can every node serve reads?

A node does not need to own the entire durable dataset. It needs access to the appropriate snapshot, relevant recent mutations, and the pages required by the query.

The node can fetch missing immutable pages and cache them.

Importantly, this architecture does not imply that an arbitrarily lagging node may return arbitrarily stale data while claiming to provide a current read. A node must satisfy the requested snapshot and freshness requirements. The implementation uses observed log positions and version information to establish which state can safely be served.

**Snapshot isolation and freshness are also different concerns.** A consistent snapshot guarantees a coherent view at a particular point; it does not automatically mean every read is linearizable. SurrealDS additionally exposes freshness controls for some reads.

## 5. Copy-on-write trees: making object storage practical

Traditional mutable storage engines frequently update pages in place.

That approach is inconvenient for object storage because object stores are primarily optimized for storing and retrieving objects, not performing small random writes within a larger file.

SurrealDS instead publishes immutable, content-addressed pages using copy-on-write structures.

Consider a simplified tree:

```text
Version 1

            Root R1
               |
       +-------+-------+
       |               |
      P1              P2
   +---+---+       +---+---+
   |       |       |       |
   A       B       C       D
```

Now suppose page B changes.

Rather than mutating B in place, the storage engine constructs a new path for the modified state.

```text
Version 1                           Version 2

            Root R1                             Root R2
               |                                   |
       +-------+-------+                   +-------+-------+
       |               |                   |               |
      P1              P2                  P1'             P2
   +---+---+       +---+---+           +---+---+       +---+---+
   |       |       |       |           |       |       |       |
   A       B       C       D           A      B'       C       D

                                       ^
                                       |
                            Unchanged pages reused
```

In a real copy-on-write tree, updated ancestors are also recreated as necessary, while unchanged subtrees remain shared.

This produces several benefits.

**Immutability simplifies caching.** A page identified by its content can remain valid indefinitely for that content. A cache does not need to invalidate it because another node modified the same page in place.

**Structural sharing reduces writes.** Rebuilding one part of a tree does not require rewriting all unrelated pages.

**Publishing a new root establishes a database version.** Readers using an existing root can continue seeing the old state while newer snapshots reference the new root.

SurrealDS periodically incorporates logged changes into tree pages and publishes an updated manifest in object storage. Its object-store configuration requires conditional writes, which are useful for coordinating updates to shared metadata.

### The hidden tradeoff: garbage collection

Copy-on-write storage creates obsolete versions of pages.

```text
Root R1 ----> Old pages
Root R2 ----> Some old + some new pages
Root R3 ----> Current pages
```

Eventually, the system must decide which old roots or pages remain reachable and which can be reclaimed.

That introduces engineering concerns involving retention, reference tracking or reachability analysis, background cleanup, and long-running snapshots.

**Content addressing makes sharing possible, but it does not eliminate the lifecycle-management problem.**

Furthermore, retaining multiple historical roots does not automatically expose unlimited time-travel queries. SurrealDS versioned reads are disabled by default.

## 6. Fault tolerance: failover is a correctness problem

Distributed databases must account for failures occurring at arbitrary points in a transaction.

A particularly difficult scenario is when the sequencer crashes immediately after acknowledging a commit.

### Scenario: losing the sequencer

Assume three nodes across three availability zones.

```text
Before failure

    AZ A                    AZ B                    AZ C
+-----------+           +-----------+           +-----------+
| Node A    |           | Node B    |           | Node C    |
| Sequencer |---------->| Witness   |           | Listener  |
|           |    Log    |           |           |           |
+-----------+           +-----------+           +-----------+

       Committed log retained
        in both AZ A and AZ B
```

Now AZ A disappears.

```text
After failure

    AZ A                    AZ B                    AZ C
+-----------+           +-----------+           +-----------+
| FAILED    |           | Node B    |           | Node C    |
|           |           | Sequencer |---------->| Witness   |
+-----------+           +-----------+           +-----------+
                              |
                              v
                       Resume commits
                       after recovery
```

The surviving nodes cannot simply select a new sequencer and immediately accept transactions.

They must first establish that the new sequencing authority has the required committed state.

The safety condition is:

**A transaction already acknowledged to a client must not disappear from the database history after failover.**

A successful transition therefore requires coordination, log-state verification, repair when necessary, and protection against conflicting sequencing authorities.

SurrealDS uses a coordinated succession protocol that verifies and repairs state before resuming service.

### Why are three availability zones important?

The default durability policy requires two copies of acknowledged writes in distinct zones.

With two nodes in two zones, losing either one leaves only one available log holder.

With three nodes in three zones, losing one still leaves two zones that can assume the sequencer and witness roles.

This is not the same as claiming that the system synchronously replicates every commit to all three nodes before acknowledgment.

**The requirement is durability on the sequencer and an acking witness in separate zones.**

### Correctness versus availability

Suppose a network partition prevents the sequencer from reaching a witness in another zone.

There are two possible policies:

| Policy                  | Behavior                                                              | Tradeoff                                                                                     |
| ----------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `mandate-two` (default) | Refuse client operations when the required second zone is unavailable | Preserves the two-zone durability requirement, sacrificing availability                      |
| `allow-one`             | Continue writing with one log copy                                    | Increases availability but allows acknowledged writes to be vulnerable to a single-node loss |

The default is explicitly conservative.

This represents a fundamental engineering principle:

**Availability is not simply the ability to respond to requests. It is the ability to respond while preserving the system's promised guarantees.**

A successful response containing incorrect or uncommitted data can be worse than a deliberate refusal.

Another subtlety is that cross-zone durability depends on correctly identifying independent failure domains. Two nodes with different labels but the same underlying power or networking dependency do not provide genuine failure independence.

## 7. Transaction isolation: ordering does not eliminate conflicts

The sequencer establishes transaction order, but transaction correctness also depends on isolation.

SurrealDS supports snapshot isolation by default, with serializable isolation available when explicitly requested.

Consider two transactions checking whether a resource is available.

```text
Initial state:
  available_resources = 1

     Transaction T1                      Transaction T2
            |                                   |
   Read available = 1                  Read available = 1
            |                                   |
   Allocate resource A                 Allocate resource B
            |                                   |
         Commit                              Commit
```

If each transaction modifies different records, snapshot isolation may permit both to commit, even though their combined result violates an application invariant.

This is a classic write-skew anomaly.

Under serializable isolation, the system validates the transaction's read set, including relevant ranges, during commit.

If concurrent changes invalidate the snapshot assumptions, the conflicting transaction is rejected and can be retried.

```text
T1 reads snapshot S             T2 reads snapshot S
         |                               |
         +---------------+---------------+
                         |
                         v
                 Concurrent writes
                         |
                         v
                 Commit validation
                         |
         +---------------+---------------+
         |                               |
        T1                              T2
      Commit                         Conflict
                                         |
                                         v
                                       Retry
```

This is an optimistic concurrency approach: allow speculative execution, then reject conflicting execution histories.

The tradeoff is that serializable transactions can experience more conflicts, particularly for hot records or broad range reads.

**The engineering lesson is that deterministic log ordering, storage durability, snapshot isolation, and serializability are distinct responsibilities.** A robust transactional system needs explicit mechanisms for each.

## 8. What actually scales, and what does not?

One of the most important distinctions in SurrealDS is that separating compute and storage does not automatically mean that all kinds of throughput scale linearly.

The architecture has different scaling properties across its components.

| Dimension            | Scaling behavior                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| Storage capacity     | Grows through shared object storage                                                                     |
| Query computation    | Additional nodes increase aggregate capacity                                                            |
| Cached read capacity | Additional nodes provide more cache and execution resources                                             |
| Commit throughput    | Limited by the single sequencer per group and its replication path                                      |
| Recovery             | Doesn't require copying a full database replica, but still requires safe log recovery and cache warming |

**Adding nodes does not itself increase the group's write capacity.**

### Why the sequencer matters

A simplified throughput bound is:

```text
Commit throughput <= Sequencer's sustainable commit-processing rate
```

That rate depends on several factors, including validation work, log append throughput, batching behavior, cross-zone replication, and disk synchronization.

Additional read-serving nodes do not remove that constraint.

```text
3 compute nodes                  12 compute nodes
       |                                 |
       v                                 v
  More reads                        More reads
       |                                 |
       v                                 v
 One sequencer                     One sequencer
       |                                 |
       v                                 v
  Commit log                        Commit log
```

That does not mean the database cannot handle substantial write throughput. It means write scalability cannot be inferred solely from the number of compute nodes.

**Compute disaggregation solves resource coupling, not every bottleneck in the system.**

A workload dominated by parallelizable queries may benefit significantly from additional nodes. A workload dominated by sustained writes may eventually encounter the limits of commit serialization.

### Another tradeoff: cache locality

The system also exchanges some local-storage simplicity for a dependence on effective caching.

A warm node may serve most reads without accessing object storage.

A newly created node may need to fetch many immutable pages before its cache becomes effective.

```text
Warm node:

Query -> Memory -> Result


Cold node:

Query -> Memory miss
              |
              v
          Disk miss
              |
              v
        Object store
              |
              v
       Populate cache
              |
              v
           Result
```

**Consequently, compute elasticity is not equivalent to instant performance elasticity.**

Adding a node can be operationally lightweight relative to copying an entire replica, but the node still needs to establish useful cache locality.

This is an important consideration for systems experiencing bursty workloads.

## 9. Engineering decisions and their tradeoffs

The architecture can be understood as a set of deliberate exchanges.

| Design decision               | Rationale                                                        | Cost or limitation                                                     |
| ----------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Shared object storage         | Decouple dataset capacity from compute nodes                     | Remote access latency, request costs, dependency on object storage     |
| Replicated local commit logs  | Keep remote object storage out of synchronous commits            | Local disk durability and cross-zone replication remain critical       |
| Single sequencer per group    | Establish a common transaction order                             | Potential commit-throughput bottleneck and succession complexity       |
| Read execution on every node  | Distribute read and query workloads                              | Need snapshot tracking, log visibility, and cache management           |
| Immutable copy-on-write pages | Efficient caching and structural sharing                         | Write amplification, metadata management, garbage collection           |
| Two-zone acknowledgment       | Survive a single-zone failure without losing acknowledged writes | Cross-zone latency and reduced availability when redundancy is missing |
| Optimistic isolation          | Avoid holding locks during transaction execution                 | Commit conflicts and retries                                           |
| Coordinated failover          | Protect committed history from stale or conflicting ownership    | Recovery complexity and possible temporary unavailability              |

None of these techniques eliminates the fundamental distributed systems tradeoffs.

The architecture chooses where those costs occur.

For example, moving object-store writes out of the commit path improves latency characteristics, but creates an interval in which recent durable commits still depend on replicated local logs.

Similarly, immutable pages simplify distributed caching but require more sophisticated lifecycle management.

## 10. Operational architecture is part of the storage architecture

SurrealDS also treats cluster management as a stateful protocol problem.

Its Kubernetes operator handles placement, local persistent volumes, peer communication, health probes, scaling, and configuration changes.

Version upgrades must account for compatibility between participating nodes. Some changes can be applied through rolling updates, while incompatible storage or communication formats may require coordinated restarts.

This matters because traditional orchestration abstractions are not sufficient on their own.

```text
      Kubernetes
           |
           v
      Pod running
           |
           X Not enough to declare database readiness
           |
           v
Storage protocol state
           |
           +-- Required log state available?
           |
           +-- Sequencer ownership established?
           |
           +-- Required durability policy satisfied?
           |
           +-- Node able to serve correct snapshots?
           |
           v
    Ready to serve
```

A live process may not be a safe participant in database operations.

**The distinction between liveness, readiness, and protocol correctness is essential for operating stateful distributed systems.**

The same applies to testing. SurrealDS uses deterministic simulation, formal protocol models, and fault injection to investigate behavior under partitions, crashes, and recovery interruptions. The architectural reason is straightforward: most serious distributed storage bugs occur in transitions between otherwise valid states.

## 11. The most important engineering lessons

1. **Separate compute locality from data ownership.**

A compute node should not necessarily own the only authoritative representation of the data it processes. Shared persistence enables flexible compute placement, while local caching recovers much of the performance benefit of locality.

2. **Separate the transaction representation from the storage representation.**

A durable, ordered log is well suited to commits and replication. An immutable indexed tree is well suited to retrieval and persistence. Converting between them asynchronously allows each representation to optimize for a different purpose.

3. **Make the acknowledgment boundary explicit.**

A transaction should be acknowledged only after the system has satisfied its promised durability requirements. This boundary must be precisely defined; merely completing a write system call or transmitting a replication message is not enough.

4. **Make recovery a protocol, not a file-copy operation.**

Recovery means reconstructing a valid committed history and establishing safe ownership. Restoring files is only part of that problem. Log verification, succession, repair, and coordination are equally important.

5. **Immutable data structures are powerful distributed systems primitives.**

Immutability reduces cache-coherence complexity, facilitates structural sharing, and makes versioned reads easier to reason about. The tradeoff moves to publication, reclamation, and metadata management.

6. **Scale independent dimensions independently.**

Storage capacity, query execution, cached reads, and write serialization are different dimensions. An architecture may scale some dimensions horizontally while preserving a deliberate bottleneck in another.

7. **Favor explicit degradation over silent correctness violations.**

If the cluster cannot establish whether its state is safe, refusing operations can be the correct behavior. Configurable weaker durability policies are possible, but they should be acknowledged as changes to the system's guarantees.

8. **Design around failure transitions from the beginning.**

Normal-operation performance is only one part of a distributed storage engine. The harder questions concern interrupted commits, simultaneous failures, stale ownership, slow recovery, incompatible upgrades, and partitions.

## 12. Final architectural interpretation

SurrealDS can be summarized as three cooperating mechanisms:

```text
               TRANSACTION LAYER

                Any Query Node
                       |
                       v
                   Sequencer
                       |
                       v
                  Ordered Log
                       |
                       v
                Cross-Zone Copy
                       |
                       v
                Durable Commit

===================================================

                  READ LAYER

                  Query Node
                       |
                       v
                Pinned Snapshot
                       |
        +--------------+--------------+
        |                             |
 Recent Changes                Persistent Tree
        |                             |
        +--------------+--------------+
                       |
                       v
                 Visible Data

===================================================

               PERSISTENCE LAYER

                Committed Logs
                       |
                       v
               Background Merge
                       |
                       v
              Copy-on-Write Tree
                       |
                       v
                Immutable Pages
                       |
                       v
              Published Manifest
                       |
                       v
                Object Storage
```

The first mechanism establishes ordering and durability. The second makes data accessible without routing every read through the sequencer. The third converts recent transactional changes into a persistent, shareable representation.

**The deepest engineering lesson is that disaggregated storage doesn't mean removing state from compute nodes. It means distinguishing transient working state, replicated transactional state, and long-term persistent state, then giving each a different placement, consistency, and recovery strategy.**

That separation enables elasticity, but correctness still depends on the protocols connecting those layers.
