# Distributed Git storage

A Git hosting service must handle pushes, fetches, and other operations from many users and agents. A busy repository may receive many requests at once.

**The challenge is to process those requests concurrently without losing data or allowing conflicting updates to overwrite one another.**

A repository-wide lock can protect shared state, but it also makes unrelated writers wait. Keeping a full durable copy on every compute node creates another cost: adding request-processing capacity also requires copying repository data.

The architecture described here addresses these problems with two principles:

1. **Minimize coordination:** Only operations that modify shared mutable state should require distributed agreement.
2. **Decouple storage from compute:** Durability, request processing, and background maintenance should scale independently.

The result is a storage system where thousands of writers can modify the same logical repository concurrently, without requiring every write to coordinate with every other write.

## 1. The fundamental architectural idea

A Git repository has two fundamentally different kinds of state.

**Immutable data:** Commits, trees, blobs, and packs. Once written, their contents never change.

**Mutable metadata:** References (branches and tags) that point to Git objects, and the manifest describing which packs belong to the repository.

These have different storage requirements.

```text
                    Git Repository
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
 IMMUTABLE DATA                       MUTABLE METADATA
        |                                     |
 Commits, trees,                      Branch references
blobs, packfiles                        Pack manifest
        |                                     |
        v                                     v
 Object Storage                        Replicated Log
        |                                     |
 Parallel writes                      Transactional CAS
 High throughput                     Strong consistency
 No shared lock                      Quorum replication
```

**The architectural insight is that most of the data in a write does not require consensus.**

For example, two workers creating different commits can upload their objects independently. They only need coordination when publishing changes to mutable references.

Consequently, the system separates the data path from the coordination path.

## 2. High-level architecture

```text
                              CLIENTS
                          Git / API / Web
                                 |
                                 v
                      +---------------------+
                      |   REQUEST ROUTER    |
                      |                     |
                      | Routing, placement, |
                      | balancing, fairness |
                      +---------------------+
                                 |
       +-------------------------+-------------------------+
       |                         |                         |
       v                         v                         v
 +-----------+             +-----------+             +-----------+
 | Replica A |             | Replica B |             | Replica C |
 |           |             |           |             |           |
 |  Compute  |             |  Compute  |             |  Compute  |
 |   Cache   |             |   Cache   |             |   Cache   |
 +-----------+             +-----------+             +-----------+
       |                         |                         |
       +-------------------------+-------------------------+
                                 |
           +---------------------+---------------------+
           |                                           |
           v                                           v
+--------------------+                      +--------------------+
| METADATA SERVICE   |                      | OBJECT STORAGE     |
|                    |                      |                    |
| Replicated log     |                      | Immutable packs    |
| Reference CAS      |                      | Pack indexes       |
| Pack manifest      |                      | Read accelerators  |
| Version / LSN      |                      | Checkpoints        |
+--------------------+                      +--------------------+
           ^                                           ^
           |                                           |
           |             +---------------+             |
           +-------------| MAINTENANCE   |-------------+
                         |               |
                         | Compaction    |
                         | Garbage       |
                         | collection    |
                         +---------------+
```

The architecture has five logical components:

- Router: Decides which compute replica handles a request.
- Virtual replicas: Execute Git operations and maintain disposable local caches.
- Object storage: Holds the durable object data.
- Metadata service: Provides transactional updates to references and the pack manifest.
- Maintenance workers: Perform compaction and garbage collection separately from foreground requests.

**No compute replica is authoritative for repository data.**

This is the key property enabling independent compute scaling.

## 3. Virtual replicas: compute without ownership

A virtual replica is a compute node capable of servicing requests for a repository.

It performs tasks such as:

- Processing pushes and fetches.
- Indexing incoming Git packs.
- Validating object connectivity.
- Executing Git operations.
- Caching repository data locally.

**Its local disk is a reconstructible cache, not the durable source of truth.**

Consider three replicas serving one repository:

```text
              Repository R
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
Replica A       Replica B       Replica C
    |               |               |
 Cache A         Cache B         Cache C
    |               |               |
    +---------------+---------------+
                    |
                    v
             Shared durable
                  state
```

Replica A does not need to communicate directly with Replica B to replicate every object write.

Both can access shared durable state.

### Why this matters

In traditional stateful replication, adding a node often means another full copy of the data and potentially another participant in replication.

With virtual replicas, adding a node primarily increases compute capacity.

```text
Increased request traffic
            |
            v
  Add virtual replicas
            |
            v
    More parallel CPU
   More read capacity
  More write processing
```

Durable storage does not need to be replicated again for every new compute replica.

### But locality still matters

Completely random request routing would be inefficient.

Imagine a 50 GB repository and a pool of replicas with cold caches. If requests continuously jump between replicas, they repeatedly fetch the same packs from object storage.

Instead, the router maintains soft affinity.

Requests for a repository preferentially go to a small set of replicas that already have useful cached data.

```text
                     Repository R
                           |
                           v
                 Preferred replica set
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
A (warm cache)      B (warm cache)      C (warm cache)
```

**The affinity is a performance optimization, not a correctness dependency.**

If Replica A fails, another replica can serve the request and reconstruct missing cache state.

This distinction is important:

**Logical ownership of a request does not imply ownership of its durable data.**

## 4. The write path: persist first, publish second

A push can be separated into two phases.

The first phase stores the new objects durably.

The second phase atomically publishes the new repository state.

```text
     Client
        |
        | PUSH
        v
 Virtual Replica
        |
        | 1. Receive objects
        | 2. Index pack
        | 3. Validate objects
        |
        v
 Object Storage
        |
        | 4. Upload pack and index
        | 5. Confirm durable storage
        |
        v
Metadata Service
        |
        | 6. Validate reference preconditions
        | 7. Commit reference update
        | 8. Add pack to manifest
        |
        v
 Push committed
```

### Phase A: Write immutable data

New objects are uploaded independently into object storage.

Suppose three workers create independent commits:

```text
Worker A ------> Pack A ------+
                              |
Worker B ------> Pack B ------+----> Object Storage
                              |
Worker C ------> Pack C ------+
```

These uploads can happen in parallel.

They do not need a global repository lock because the stored objects are immutable.

### Phase B: Publish the metadata transaction

Once the pack is durable, the virtual replica submits a transaction to the metadata service.

Conceptually:

```text
Transaction:
    Expected:
        refs/heads/feature = C1

    Changes:
        refs/heads/feature = C2
        manifest += Pack P

    Commit if preconditions hold.
```

The metadata service commits this change through its replicated log.

Only after the commit becomes visible does the new reference point at the uploaded objects.

### Why this ordering matters

Consider the reverse order:

```text
1. Publish reference C2
2. Upload objects for C2
```

If the second step fails, the repository contains a reference pointing to unavailable data.

That is a correctness failure.

Instead:

```text
1. Persist objects for C2
2. Publish reference C2
```

If the first step succeeds but the second fails, unreferenced objects may remain in storage.

These objects can be reclaimed later.

**Orphaned durable objects are preferable to committed references pointing at missing objects.**

**This is a broadly useful distributed storage pattern: prepare immutable data first, then atomically publish metadata that makes it reachable.**

## 5. Metadata service: coordination at reference granularity

This is the most important consistency component.

The service maintains a replicated transaction log and supports compare-and-swap (CAS) updates.

Every mutation checks expected reference values before committing.

For example:

```text
Current state:

main    -> C10
feature -> C20
dev     -> C30
```

Two concurrent transactions arrive:

```text
Transaction A:
    feature C20 -> C21

Transaction B:
    dev C30 -> C31
```

These operations are independent.

There is no need to serialize their object processing or force one to wait for the other reference's lock.

```text
Time ---------------------------------------->

Transaction A: [ check feature ][ commit ]
Transaction B: [ check dev     ][ commit ]
```

Although commits receive positions in the replicated log, their precondition checks and nonconflicting reference operations can proceed concurrently.

### What happens when writers conflict?

Suppose two transactions try to modify `main`:

```text
Initial state:

main -> C10
```

```text
  Writer A                        Writer B
      |                               |
Expected C10                    Expected C10
New value C11                   New value C12
      |                               |
      +---------------+---------------+
                      |
                      v
                Metadata CAS
                      |
        +-------------+-------------+
        |                           |
        v                           v
  Writer A wins              Writer B fails
        |                           |
   main -> C11                precondition
```

The second writer must retry or resolve the conflict according to the Git operation's semantics.

This prevents lost updates.

### Multi-reference transactions

Some operations update several references.

A transaction may need to modify:

```text
refs/heads/main
refs/heads/release
```

The metadata service can validate and update both atomically.

That requires locking the references touched by the transaction, rather than locking the entire repository.

### What does the replicated log provide?

Each committed transaction receives a log sequence number (LSN).

For example:

```text
LSN 100: feature -> C21
LSN 101: dev     -> C31
LSN 102: main    -> C11
```

The latest LSN represents the repository metadata version.

The log provides:

- Durable ordering of committed metadata changes.
- A version for detecting stale replicas.
- Atomic reference transactions.
- Quorum-backed visibility.
- A way to synchronize replicas with current metadata.

There is a subtle distinction here:

**The architecture does not require a separate consensus group for every branch.**

Instead, it uses a shared replicated metadata service with fine-grained concurrency control.

Independent references avoid locking each other even though transactions are recorded in an ordered log.

## 6. The read path: version checking and lazy synchronization

A virtual replica may hold stale cached metadata or lack recently uploaded packs.

A read must first determine whether its view is current.

The architecture uses repository version checks.

```text
                        READ REQUEST
                              |
                              v
                       Virtual Replica
                              |
                              v
                        Local LSN=100
                              |
                              v
                      Metadata Service
                              |
                              v
                      Current LSN=100?
                              |
      +-----------------------+-----------------------+
      |                                               |
     YES                                             NO
      |                                               |
      v                                               v
Cached state                                   Return current
 is current                                   metadata and LSN
      |                                               |
      |                                               v
      |                                       Identify required
      |                                           pack data
      |                                               |
      |                                               v
      |                                         Fetch missing
      |                                       packs into cache
      |                                               |
      +-----------------------+-----------------------+
                              |
                              v
                         Serve read
```

### Fast path: no changes

Suppose a replica last observed version 100.

The authoritative metadata version is still 100.

The service can reply that nothing changed without retransmitting the reference set.

This makes repeated reads relatively cheap.

Instead of transferring potentially large metadata structures, the read requires a version comparison.

### Slow path: replica is behind

Suppose the replica has version 100 but the authoritative version is 105.

The metadata service returns updated reference state, the current version, and relevant pack information.

The replica then retrieves the missing packs needed for its operation.

Importantly, the metadata check and object download solve different problems:

- Metadata synchronization establishes which repository state is current.
- Object synchronization ensures the replica has the data required to serve that state.

### Why the version is important

Without a repository-level version, the system might need to check many references independently.

For example:

```text
Check main?
Check feature-a?
Check feature-b?
Check release?
Check dev?
...
```

The version acts as a compact indication that the repository state has changed.

It does not eliminate the need to retrieve changed metadata. It makes the overwhelmingly common unchanged case cheap.

### The tradeoff

The architecture replaces continuous full replication to every compute replica with on-demand cache synchronization.

This improves flexibility but introduces the possibility of cache misses and object-storage reads on the request path.

Fast reads depend on useful caches, efficient indexes, and good routing affinity.

## 7. Compaction: avoiding unbounded read amplification

The write architecture creates another problem.

Every push introduces a new Git pack.

Suppose a repository receives 5,000 pushes per second, with one new pack per push.

Without maintenance:

```text
After 1 second:        5,000 packs
After 1 minute:      300,000 packs
After 1 hour:     18,000,000 packs
```

These are illustrative counts, but the consequence is real.

Git can search across multiple packs, but an increasing number of packs makes indexing and object lookup more expensive.

The architecture therefore needs continuous compaction.

### Compaction as an independent subsystem

Compaction runs on separate workers, not on request-serving replicas.

```text
            Object Storage
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
Pack A          Pack B          Pack C
   |               |               |
   +---------------+---------------+
                   |
                   v
           Compaction Worker
                   |
                   v
            New merged pack
                   |
                   v
            Object Storage
                   |
                   v
         Update pack manifest
```

The system must be able to compact while writers continue adding new packs.

It cannot simply pause all pushes until compaction finishes.

### Sharded compaction

Packs are assigned to compaction shards by hash.

Each worker acquires a lease for a shard.

```text
                  PACKS
                    |
                    v
           Hash-based sharding
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
 Shard 0         Shard 1         Shard 2
    |               |               |
    v               v               v
Worker A        Worker B        Worker C
    |               |               |
    v               v               v
 Compact         Compact         Compact
```

The lease ensures that only one worker owns compaction work for a particular shard at a time.

Different shards can be processed in parallel.

### Segments and tiered merging

Each shard accumulates new packs in an open segment.

When a threshold based on size, count, or age is reached, the segment is sealed.

```text
  Incoming packs
         |
         v
+-----------------+
| Open Segment    |
| P1 P2 P3 P4     |
+-----------------+
         |
         | Threshold reached
         v
+-----------------+
| Sealed Segment  |
| P1 P2 P3 P4     |
+-----------------+
         |
         v
    Compaction
         |
         v
+-----------------+
| Merged Pack P5  |
+-----------------+
```

While a sealed segment is compacted, another open segment can collect incoming packs.

Smaller compacted packs can be merged again in subsequent rounds, until they reach the configured size limit.

This resembles tiered compaction in log-structured storage systems.

### Safely publishing compacted packs

Compaction cannot replace the manifest entries before the new pack is durable.

The safe sequence is:

1. Read input packs.
2. Produce merged packs.
3. Verify that the output contains exactly the same objects.
4. Upload the new packs.
5. Add new packs to the manifest.
6. Remove old packs from the manifest in a subsequent transaction.
7. Delete obsolete pack data later.

Notice the use of two metadata transactions.

```text
Before:

Manifest = {P1, P2, P3}

After new pack is added:

Manifest = {P1, P2, P3, P4}

After old packs are retired:

Manifest = {P4}
```

This creates a temporary period of redundancy, but prevents readers from encountering a manifest that references missing replacement data.

The general principle is:

**Publish new state before retiring old state.**

The cleanup phase must also respect readers that may still be using old packs.

## 8. Garbage collection is different from compaction

**Compaction and garbage collection solve different problems.**

Compaction reduces the number of packs while preserving their objects.

Garbage collection removes objects that are no longer reachable from retained references and other protected roots.

Consider:

```text
main -> C3 -> C2 -> C1

old  -> C4 -> C2
```

Deleting the `old` reference could eventually make `C4` unreachable.

However, safe garbage collection in a concurrent system requires special care.

A collection cycle must not delete an object that is still needed by:

- A concurrent reference update.
- A reader using an older valid view.
- An in-progress push.
- A retention or recovery policy.

The design uses dedicated maintenance workers and durable records to coordinate and resume maintenance work, but the detailed garbage-collection safety protocol is not fully specified.

The architectural takeaway is that garbage collection is a separate, correctness-sensitive lifecycle problem, not merely pack merging.

## 9. Why not store all metadata directly in object storage?

Object storage often supports conditional writes.

A natural design is to store a reference-state blob and use conditional writes to implement CAS.

That sounds simpler than maintaining a separate replicated log.

But it creates a throughput problem.

### Option A: One metadata blob

```text
    Writers
       |
       v
+-------------+
| Single Blob |
|             |
|  All refs   |
+-------------+
```

Every metadata transaction competes to update the same blob.

Only one conditional write to that blob can proceed at a time.

Advantages:

- Simple consistency model.
- Cheap unchanged-state reads.
- No separate metadata consensus service.

Disadvantage:

- Repository-wide write serialization.

Batching helps, but does not remove the serialized round-trip ceiling.

### Option B: Partition references across blobs

```text
           Reference Hashing
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
Blob A          Blob B          Blob C
   |               |               |
Refs A          Refs B          Refs C
```

Independent reference updates can now proceed concurrently.

But checking whether a repository changed requires consulting multiple segments.

As the number of segments increases, read amplification grows, and the slowest segment can determine response latency.

This is particularly problematic when reads greatly outnumber writes.

### Option C: Dedicated transactional metadata log

The chosen design is a small, replicated service optimized for metadata updates.

It supports:

- Fine-grained reference locking.
- High concurrency for nonconflicting writes.
- Atomic updates across several references.
- A repository-wide version for cheap reads.
- Quorum-backed durability.

The tradeoff is additional distributed systems complexity and a metadata service on the critical path of every published mutation.

**The design deliberately concentrates coordination in one small subsystem rather than spreading it across the bulk-data infrastructure.**

## 10. Failure handling and operational tradeoffs

Separation of responsibilities improves fault isolation, but it does not make failures disappear.

| Failure                                          | Architectural behavior                                                |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| Compute replica crashes                          | Another replica can serve the request and rebuild cache state         |
| Upload succeeds, metadata commit fails           | Uploaded objects remain unpublished; cleanup can reclaim them         |
| Metadata commit succeeds, acknowledgment is lost | Client may face an ambiguous result; retry must check committed state |
| Two writers update the same reference            | CAS detects the conflict                                              |
| Compaction worker crashes                        | Durable work records and leases support resumption                    |
| Cache miss                                       | Replica retrieves necessary data from object storage                  |
| Metadata quorum unavailable                      | Reference commits cannot safely proceed                               |

The biggest tradeoffs are:

**Higher dependency on the metadata service.** It is deliberately small, but remains essential for publishing and synchronizing current repository state.

**More cold-cache latency.** Disposable replicas improve elasticity and recovery, but may need to retrieve substantial data before serving requests efficiently.

**More complex lifecycle management.** Immutable objects simplify writes, but abandoned uploads, compaction outputs, and unreachable objects need careful cleanup.

**More object-storage traffic.** Write concurrency is easier to scale, but each new pack, compaction operation, and cold read adds storage operations and potentially network transfer.

**A need for continuous maintenance capacity.** Write throughput can grow faster than compaction throughput. If that happens, pack counts and read amplification eventually increase.

**The maintenance subsystem must therefore scale with the rate at which incoming writes generate new packs.**

## 11. The overall architectural pattern

The complete system can be understood as three cooperating planes.

```text
     +--------------------------------------------------+
     |                   COMPUTE PLANE                  |
     |                                                  |
     | Routing -> Virtual Replicas -> Git Operations    |
     |                                                  |
     | Scales with requests and CPU-intensive work      |
     +--------------------------------------------------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
+--------------------------+      +--------------------------+
|    COORDINATION PLANE    |      |       STORAGE PLANE      |
|                          |      |                          |
| Reference CAS ->         |      | Immutable Packs /        |
| Replicated Metadata Log  |      | Indexes / Auxiliary Data |
|                          |      |                          |
| Orders mutations and     |      | Scales with bytes and    |
| publishes durable state  |      | aggregate I/O            |
+--------------------------+      +--------------------------+
              ^                                 ^
              |                                 |
              |  +---------------------------+  |
              +--|     MAINTENANCE PLANE     |--+
                 |                           |
                 | Compaction / GC Workers   |
                 |                           |
                 | Independently scalable    |
                 +---------------------------+
```

The coordination and storage planes are logically separate; the diagram is not intended to imply that all object I/O passes through the metadata service.

### Engineering lessons

The architecture illustrates several reusable practices.

1. **Coordinate at the smallest correct granularity.** If independent entities can be modified independently, a coarse global lock creates unnecessary contention.
2. **Separate immutable bulk data from mutable metadata.** Immutable data can often use simpler, massively parallel storage protocols, while small mutable state benefits from stronger transactional mechanisms.
3. **Use metadata publication as the commit point.** Make data durable before exposing pointers to it. This reduces the amount of work requiring distributed agreement.
4. **Treat caches as disposable, but preserve locality.** Correctness should not depend on cache placement, while performance often should.
5. **Scale maintenance separately from foreground traffic.** Compaction and garbage collection consume substantial resources and should not compete directly with latency-sensitive requests.
6. **Optimize for the read/write ratio, not writes alone.** Sharding mutable metadata can improve write throughput while increasing the cost of every read. A good design must account for total workload amplification.
7. **Design for continuously changing physical layout.** Readers and writers must remain correct while background processes reorganize the underlying objects.

**The essential idea is that a repository no longer needs to behave like a single stateful machine that every writer must visit and lock.**

It becomes a logical object assembled from immutable data and transactional metadata, with compute replicas acting as interchangeable execution resources.

That pattern extends far beyond Git storage: it applies to object-backed databases, distributed metadata systems, analytical storage engines, and other architectures where large amounts of immutable data are made visible through a much smaller, strongly consistent control structure.
