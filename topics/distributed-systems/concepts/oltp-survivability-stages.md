# Seven stages of OLTP survivability

The seven stages of OLTP survivability are a model for reasoning about how a
transaction engine changes as its durable state grows. Each stage removes one
recovery limit, but exposes another.

The progression is not a law that every database follows. It is most useful
for strict-serializable, write-heavy workloads with hot keys and demanding
recovery objectives.

The core idea is:

> **An OLTP architecture stops scaling when it can no longer restore healthy
> redundancy faster than failures consume it.**

## The progression at a glance

| Stage | Architecture             | Problem solved             | Next limit               |
|------:|--------------------------|----------------------------|--------------------------|
|     1 | Append-only log          | Durable ordered writes     | Unbounded replay         |
|     2 | Log plus snapshots       | Shorter replay             | Snapshot and memory size |
|     3 | LSM storage engine       | Capacity beyond RAM        | Single-node recovery     |
|     4 | Replicated state machine | Individual node failure    | Replica rebuild time     |
|     5 | Sharded RSMs             | Bounded state per shard    | Cross-shard coordination |
|     6 | Disaggregated storage    | Elastic durable capacity   | Remote-storage latency   |
|     7 | RSM + LSM + object store | Bounded hot recovery state | Tiering complexity       |

The stages are easiest to understand as a sequence of changing bottlenecks:

```text
log replay
    -> snapshot size
    -> machine size
    -> replica rebuild
    -> cross-shard coordination
    -> remote-storage latency
    -> bounded local state plus tiering
```

## Stage 1: the pure log

The first design keeps the database in memory and appends every committed
transaction to a durable log.

```text
transaction -> append to log -> update memory -> acknowledge
```

The log provides order, durability, and a recovery history. After a crash, the
engine reconstructs memory by replaying every entry.

This works until the history becomes too long. If the log grows with the
lifetime of the database, then restart time grows with it. Durability has been
solved, but recovery work remains unbounded.

## Stage 2: snapshots

A snapshot records the materialized state at a particular log position.
Recovery can load the latest snapshot and replay only the newer suffix.

```text
full log:       [------------------------------------]

snapshot:       [materialized state]
remaining log:                      [----------------]
```

Snapshots bound replay, but creating or loading a large snapshot still costs
time and I/O. Implementations can produce snapshots in the background, from a
replica, or with copy-on-write, so snapshotting need not block all traffic.
Even then, a purely in-memory database cannot grow beyond the memory available
to one host.

## Stage 3: the LSM storage engine

An LSM tree turns snapshotting into continuous, incremental work. Recent
writes stay in memory and fast local storage; compaction moves older data into
larger, colder levels.

```text
CPU -> memory -> local NVMe
        hot        colder
```

The database can now exceed RAM and use the machine's full storage hierarchy.
The LSM also creates a natural age gradient: recent data remains near the top,
while historical data settles into deeper levels.

The new limit belongs to the deployment, not to the LSM itself. If the entire
engine lives on one machine, losing that machine means restoring all of its
state from backup. A very large local disk can take hours to rebuild.

## Stage 4: the replicated state machine

A replicated state machine masks individual machine failures. Consensus
places commands into one ordered log, and deterministic replicas apply those
commands to derive the same state.

```text
                 ordered commands
                       |
          +------------+------------+
          v            v            v
       replica A    replica B    replica C
```

If one replica fails, the others can retain quorum and continue serving. A
snapshot can then bootstrap a replacement before it catches up from the log.

Failover may be fast while repair is slow. The cluster is degraded until the
replacement has copied enough state to restore redundancy. If another failure
arrives first, quorum may be at risk.

```text
stable cluster -> one replica fails -> long rebuild -> another failure
                                                    -> possible quorum loss
```

Replication therefore changes the question from "Can one node restart?" to
"Can the cluster rebuild a replica before its failure budget is exhausted?"

## Stage 5: horizontal sharding

Sharding divides the database among several replicated state machines. Each
shard owns a bounded portion of the data, so adding shards can increase total
capacity without making every replica larger.

```text
database
   +-- shard A -> replicated state machine
   +-- shard B -> replicated state machine
   +-- shard C -> replicated state machine
```

This works especially well when transactions stay within one shard. A
transaction spanning shards, however, needs distributed coordination such as
two-phase commit, timestamp ordering, or another commit protocol.

Sharding is therefore workload-sensitive. Independent keys scale cleanly;
hot keys and cross-shard invariants preserve a serialized portion that more
machines cannot remove. The bottleneck moves from storage capacity to
coordination and locality.

## Stage 6: disaggregated storage

Disaggregation separates replaceable compute from a durable shared storage
service such as object storage.

```text
compute nodes
     |
     | network
     v
shared object storage
```

Durable capacity becomes elastic, and replacing a compute node no longer
requires it to own a complete local copy first. This simplifies one part of
recovery, but does not remove recovery altogether: caches, indexes, metadata,
and control state may still need reconstruction.

The central tradeoff is latency. An object request crosses a network and a
large distributed service. It is a good home for durable bulk data, but a poor
substitute for the memory and local NVMe on the critical path of a
latency-sensitive transaction.

## Stage 7: diagonal scaling

Diagonal scaling combines the strengths of the earlier designs instead of
choosing between one large local engine and fully remote storage.

```text
strict-serializable transactions
              |
              v
   +-----------------------+
   | bounded, replicated   |  hot: memory and local NVMe
   | LSM working set       |
   +-----------+-----------+
               |
               | tier cold LSM levels
               v
   +-----------------------+
   | object storage        |  cold: large and durable
   +-----------------------+
```

The local replicated state machine retains the hot working set needed for
low-latency execution. Deeper LSM levels move asynchronously to object
storage. Total history can grow without forcing the consensus group to keep
all of it on local disks.

This design is "diagonal" because compute and storage scale in different
directions:

| Resource | Scaling direction | Reason                                       |
|----------|-------------------|----------------------------------------------|
| Compute  | Up within an RSM  | Preserve locality for contended transactions |
| Storage  | Out to object     | Grow cold capacity independently             |

The percentages and capacities are engineering choices, not properties of the
pattern. The local bound must come from a recovery objective, the measured
rebuild rate, and enough safety margin for concurrent failures.

## What diagonal scaling does not eliminate

Tiering trades one set of problems for another:

- A cold read may pay object-storage latency.
- Compaction must operate correctly across local and remote levels.
- Cache policy determines which data remains on the fast path.
- Object-storage outages and throttling become system dependencies.
- Metadata must locate remote objects without becoming a new bottleneck.

The architecture does not guarantee microsecond latency or a particular
recovery time. It bounds the amount of local state that ordinarily needs to be
rebuilt. Wall-clock recovery still depends on bandwidth, CPU, scheduling,
surviving replicas, and foreground load.

## The survivability invariant

The seven stages lead to one durable design rule:

```text
local recovery work <= recovery capacity * recovery time budget
```

Object storage may hold a vast history, but the failure-sensitive local set
must remain small enough to recover with headroom. Scale is survivable only
while the system can restore redundancy faster than failures remove it.

---

Return to [Concepts](_index.md)
