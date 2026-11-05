# Incremental computation vs. full recalculation

A common problem in large-scale systems is that a small change can trigger an enormous amount of unnecessary work.

A system might manage millions of records, yet changing a single configuration setting causes it to read, transform, and compare the entire dataset.

This creates an architectural problem: the cost of processing a change grows with the size of the dataset rather than with the size of the change.

The natural optimization is incremental computation: recompute only the state affected by a change.

However, this introduces an important tradeoff:

**Full recomputation makes correctness relatively simple. Incremental computation makes performance better but correctness substantially harder.**

## 1. The fundamental problem: work amplification

Consider a system that maintains a materialized representation of some logical state.

For example, a configuration management system might maintain:

- 10 million configuration records.
- Shared metadata describing the configuration.
- A materialized representation optimized for fast reads.

Every change must eventually appear in the materialized representation.

```text
Source of Truth
+------------+
|  Database  |
+------------+
       |
       | Change events
       v
+------------+
| Event Log  |
+------------+
       |
       v
+------------+
|   State    |
|  Builder   |
+------------+
       |
       | Materialized state
       v
+------------+
|  Serving   |
|   Store    |
+------------+
```

The builder reads authoritative state, applies transformations, and updates the serving store.

### Approach A: Full recomputation

The simplest implementation responds to every event by rebuilding the complete logical object.

```text
 Event: change record #42
             |
             v
+------------------------+
| Read all 10M records   |
+------------------------+
             |
             v
+------------------------+
| Transform all records  |
+------------------------+
             |
             v
+------------------------+
| Compare with old state |
+------------------------+
             |
             v
+------------------------+
| Write changed keys     |
+------------------------+
```

Only one record may have changed, but the system processes 10 million records to discover that fact.

An important distinction:

**Writing only the changed records is not equivalent to processing only the changed records.**

The final write might contain one key, yet the system still performs millions of reads, transformations, allocations, and comparisons.

For a dataset containing `N` records:

```text
T_build = O(N)
```

If the implementation materializes both the source dataset and existing serving-state keys in memory, its working-set memory may also be `O(N)`.

### Approach B: Targeted recomputation

Instead of rebuilding everything, determine which outputs could have changed.

```text
 Event: change record #42
             |
             v
+------------------------+
| Determine impact scope |
+------------------------+
             |
             v
+------------------------+
| Read relevant records  |
+------------------------+
             |
             v
+------------------------+
| Recompute affected     |
| materialized keys      |
+------------------------+
             |
             v
+------------------------+
| Update serving state   |
+------------------------+
```

If a change affects `K` records, the work can approach:

```text
T_build = O(K)
```

Here `K` represents the affected output set, including relevant dependencies, and may be much smaller than `N`.

This difference becomes increasingly important as datasets grow.

But there is a problem: determining `K` correctly is not always straightforward.

## 2. Why full recomputation is architecturally attractive

Full recomputation has a very useful property: it requires relatively little knowledge about the change.

The algorithm is conceptually simple:

```text
Desired State = Build(Current Authoritative State)
```

Suppose a configuration object contains records and settings:

```text
Configuration
|
+-- Records
|   +-- A
|   +-- B
|   +-- C
|
+-- Settings
|   +-- S1
|   +-- S2
|
+-- Metadata
```

If setting `S1` changes, the builder does not need to understand which records depend on `S1`.

It reconstructs everything.

This provides several advantages:

- Changes to dependencies are less likely to be missed.
- Unknown event types can still be processed.
- Deletions and stale output can be detected through comparison.
- The system can recover from drift by reconstructing the desired state.

The tradeoff is resource consumption.

| Property              | Full recomputation         | Incremental recomputation    |
| --------------------- | -------------------------- | ---------------------------- |
| Computation           | Entire dataset             | Affected subset              |
| Memory                | Potentially large          | Usually smaller              |
| Change dependencies   | Mostly implicit            | Must be understood           |
| Unknown events        | Naturally handled          | Require fallback             |
| Stale-state cleanup   | Broad comparison           | Targeted invalidation        |
| Implementation        | Simpler                    | More complex                 |
| Correctness reasoning | Relatively straightforward | Requires stronger invariants |

Full recomputation is therefore not necessarily a bad design. It is often an excellent baseline, especially when datasets are small or changes are rare.

The problem emerges when processing cost scales with total state size while the typical change affects only a tiny fraction of that state.

## 3. The central architectural decision: separate planning from execution

A powerful design pattern is to introduce a change-impact planner.

Rather than immediately executing a rebuild, the system first determines what must be recomputed.

```text
   Change Event
         |
         v
+----------------+
| Impact Planner |
+----------------+
         |
         v
+----------------+
|   Work Plan    |
+----------------+
         |
         v
+----------------+
|   Scheduler    |
+----------------+
         |
         v
+----------------+
|    Executor    |
+----------------+
         |
         v
Materialized State
```

This separates three concerns:

Planning: What work is required for correctness?

Scheduling: When should that work run, and which work can be combined?

Execution: How should the authoritative state be read, transformed, and published?

### Different changes require different scopes

A planner can classify changes into increasingly broad categories:

| Change type                             | Required work                      |
| --------------------------------------- | ---------------------------------- |
| Ordinary record update                  | Recompute one logical resource     |
| Resource affecting shared metadata      | Recompute resource and metadata    |
| Global setting affecting a known subset | Recompute that subset and metadata |
| Object removal                          | Purge previously published state   |
| Unknown or global change                | Full recomputation                 |

Consider:

```text
Event A: Record X changes
    |
    +--> Recompute X

Event B: Shared metadata changes
    |
    +--> Recompute metadata
    +--> Recompute dependent records

Event C: Unknown configuration change
    |
    +--> Full recomputation
```

The planner is essentially an implementation of dependency-aware invalidation.

The important correctness invariant is:

```text
IncrementalBuild(S, delta) = FullBuild(Apply(S, delta))
```

This equality describes the desired resulting state, not necessarily the same intermediate operations.

**Targeted execution is safe only when it produces the same observable final output as rebuilding from scratch, including necessary deletions.**

### The tradeoff: efficiency versus dependency knowledge

Incremental computation requires knowledge about how source fields influence derived outputs.

When that knowledge is incomplete, the system risks under-invalidation: leaving old or incorrect materialized state behind.

The safe default is therefore:

**Unknown dependency means broader recomputation, not optimistic recomputation.**

That conservative fallback is a crucial architectural principle.

## 4. Events must contain enough information to support incremental work

A generic notification such as:

```text
Object #123 changed
```

is sufficient for full recomputation, but not for targeted recomputation.

The builder does not know what changed.

A more useful event contains information such as:

```text
Object: 123
Field: routing_mode
Previous: mode_a
Current: mode_b
Version: 57
```

Now the planner can reason about which outputs may be affected.

Previous values matter especially for deletions and renames.

Suppose:

```text
Old state:
    key = /services/old-name

New state:
    key = /services/new-name
```

Recomputing only the new key is insufficient.

The old key must also be removed.

```text
             Rename Event
                   |
     +-------------+-------------+
     |                           |
     v                           v
Remove old                   Write new
    key                         key
     |                           |
     +-------------+-------------+
                   |
                   v
             Correct State
```

### Architectural tradeoff

Rich events cost more to generate and maintain. Event schemas become more closely coupled to change semantics.

However, they allow downstream systems to avoid expensive discovery work.

A useful general principle:

**Information captured cheaply at mutation time can eliminate expensive computation later.**

The event stream becomes more than a notification mechanism: it becomes an input to a computation planner.

## 5. Shared metadata creates hidden dependencies

One of the more subtle problems arises when logically independent objects share derived metadata.

Imagine several objects with a common external identity:

```text
          Logical Identity: X
                   |
                   v
            Shared Metadata
                   |
    +--------------+--------------+
    |              |              |
    v              v              v
Object A       Object B       Object C
```

Updating Object B may require recomputing the shared metadata.

But Object B alone does not necessarily contain enough information to construct that metadata correctly.

For example, shared metadata may identify which objects are currently eligible for serving.

The correct strategy is to reconstruct the shared value from the current authoritative state rather than patching an old value using potentially stale assumptions.

```text
   Change to Object B
            |
            v
 Read current membership
            |
            v
Recompute shared metadata
            |
            v
Publish updated metadata
```

This introduces two important design requirements.

First, related writes need appropriate ordering. If metadata contains references to materialized resources, the referenced resources should generally be available before the metadata points to them.

Second, writers sharing the same logical key require coordination. Partitioning or serializing work by the shared identity can prevent independent workers from overwriting one another's updates.

The tradeoff is reduced parallelism for objects that share state.

This is a recurring pattern in distributed systems:

**The correct unit of concurrency is determined by the scope of shared mutable state, not necessarily by the identity of the triggering event.**

## 6. Planning from events is not enough: state can change before execution

An event describes a change that happened at some point in the past.

Execution may occur later.

```text
Time ---------------------------------------------------------------->

      T1                      T2                      T3
       |                       |                       |
 Event created           State changes          Build executes
       |                       |                       |
    Plan A                Plan A may              Revalidate
                          be outdated             assumptions
```

This creates a time-of-check/time-of-use problem.

**A plan that was valid when the event was created may no longer be valid when it runs.**

For example:

- A previously eligible object may have been disabled.
- The object's publication status may have changed.
- A feature may now require broader recomputation.
- The membership of shared metadata may have changed.

A robust architecture uses two stages:

```text
      Event
        |
        v
Conservative Plan
        |
        v
   Work Queue
        |
        v
Read Fresh State
        |
        v
Validate / Expand
        |
        v
     Execute
```

Revalidation can expand a targeted plan, transform it into a purge, or determine that some work is no longer necessary.

The tradeoff is additional database reads and complexity.

There is also a consistency challenge: an event may become visible before the corresponding database change is visible on a read replica.

A fixed delay can reduce this risk, but a stronger mechanism checks whether the replica has reached the required source position or version.

This yields another general principle:

**Use explicit consistency checks where possible instead of relying entirely on time-based safety margins.**

A fresh read is only useful if it is fresh enough.

## 7. Coalescing work: reducing redundant computation without losing events

Event-driven systems often receive several changes to the same logical object in quick succession.

Naively, each event may trigger its own build.

```text
Event A --> Build A
Event B --> Build B
Event C --> Build C
```

But if the events arrive before execution starts, their work can sometimes be combined.

```text
Event A --+
          |
Event B --+--> Merge Plans --> One Build
          |
Event C --+
```

Suppose:

```text
Plan A = {resource X}
Plan B = {resource Y, metadata}
Plan C = {resource Z}
```

The merged plan becomes:

```text
Merged = {resource X, resource Y, resource Z, metadata}
```

A useful property is that merging should be conservative.

**Adding events may increase the required work, but must not silently remove an obligation needed for correctness.**

A full rebuild subsumes targeted rebuild requests. A purge may supersede rebuild requests when the current desired state is absence.

Importantly, the work plan and event acknowledgments are separate concerns.

**Even if one build satisfies 100 events, those 100 events must remain accounted for until the corresponding work has completed safely.**

### The tradeoff: batching versus latency

Waiting intentionally to collect events improves batching efficiency but introduces delay.

Opportunistic coalescing avoids this unnecessary waiting: merge work that is already queued, then execute when scheduling constraints permit.

This provides much of the benefit of batching without imposing a fixed batching delay on every request.

## 8. Why expensive work can damage unrelated work

In an ordered event log, processing and acknowledgment are related but distinct.

A worker system might process events concurrently, yet only advance a partition's committed position once every earlier event is complete.

```text
Partition:

Offset:   10      11      12      13      14
           |       |       |       |       |
Status:  Done    Slow    Done    Done    Done
                   |
                   v
            Commit blocked

Highest contiguous completed offset = 10
```

Even though offsets 12–14 are finished, the system cannot safely commit past offset 11.

If the consumer restarts, completed-but-uncommitted messages may be replayed.

**This is head-of-line blocking at the acknowledgment boundary, not necessarily at the execution boundary.**

An expensive full rebuild can therefore create several problems simultaneously:

- Longer execution time.
- Higher memory pressure.
- Delayed acknowledgment progress.
- More work replayed after failures.
- Increased tail latency for otherwise inexpensive changes.

Targeted recomputation reduces the duration of these expensive outliers.

### Scheduling tradeoffs

A scheduler should also prevent one frequently changing object from monopolizing capacity.

Possible controls include per-object cooldown intervals, bounded concurrency, fairness policies, and retry backoff.

But delaying builds too aggressively increases propagation latency.

One useful compromise is to enforce normal per-object scheduling intervals while allowing aged work to bypass those intervals before it causes excessive log blockage.

The scheduler must balance:

```text
Efficiency <-> Freshness <-> Fairness
```

## 9. The uncomfortable tradeoff: correctness versus feasibility

Conservative planners usually fall back to full recomputation when the affected scope is uncertain.

But what happens when the dataset is too large for a full rebuild to complete?

A strict full-rebuild requirement may produce a permanently stuck object and block unrelated work.

This creates an uncomfortable situation:

```text
    Unknown Change
           |
           v
  Full Rebuild Needed
           |
           v
Dataset Exceeds Memory
           |
           v
   Repeated Failures
           |
           v
Queue Progress Blocked
```

There are several possible architectural responses.

One is to keep full recomputation but redesign it as a bounded-memory streaming or chunked algorithm. Another is to apply only the known targeted updates and provide a separate reconciliation mechanism for potentially missed state.

The second approach deliberately accepts a weaker correctness guarantee in exceptional cases to preserve system availability.

This should not be confused with proven incremental equivalence. It is a degraded operating mode requiring explicit risk assessment and repair procedures.

The deeper engineering lesson is:

**A theoretically correct fallback is not operationally useful if it can never complete.**

**Correctness, bounded resource consumption, and progress guarantees need to be considered together.**

## 10. Performance optimization should target the workload distribution

A final subtlety concerns measurement.

Suppose 95% of changes already require very little work, while 5% trigger extremely expensive builds.

Optimizing the expensive 5% might produce only a small change in median execution time.

Yet it can dramatically improve:

- Worst-case memory usage.
- Queue stability.
- Tail latency.
- Failure recovery.
- Capacity headroom.

This is why averages alone are insufficient.

A useful performance model separates processing from waiting:

```text
T_completion = T_queue + T_consistency_wait + T_execution + T_publication
```

These components can interact. Reducing expensive execution may prevent queue buildup, while freed capacity may allow shorter scheduling delays.

Consequently, an optimization can have a second-order benefit: removing expensive work makes it safe to reduce protective waiting elsewhere in the system.

Measurement should include execution times by build type, working-set memory, queue age, log lag, replay volume, and latency percentiles.

Another important practice is validating incremental results against full recomputation.

For deterministic input state, both should produce equivalent outputs. This can be tested through differential testing, shadow execution, and reconciliation, while accounting for timing differences between independent pipelines.

## 11. The architectural tradeoffs summarized

| Decision                                   | Benefit                                  | Cost or risk                                   |
| ------------------------------------------ | ---------------------------------------- | ---------------------------------------------- |
| Incremental rather than full recomputation | Much less CPU, I/O and memory            | Dependency tracking complexity                 |
| Rich events                                | Precise impact classification            | More complex event contracts                   |
| Conservative fallback                      | Protects correctness                     | Expensive full rebuilds remain                 |
| Fresh-state revalidation                   | Avoids stale planning assumptions        | Additional reads and coordination              |
| Shared-key serialization                   | Prevents conflicting updates             | Limits parallelism                             |
| Event coalescing                           | Eliminates redundant work                | More complicated scheduling and acknowledgment |
| Ordered acknowledgment                     | Protects against message loss            | Head-of-line blocking and replay               |
| Per-object scheduling limits               | Improves fairness and capacity stability | Adds freshness delay                           |
| Partial updates with reconciliation        | Preserves progress                       | May weaken completeness guarantees             |
| Differential verification                  | Catches missed dependencies              | Additional validation cost                     |

## 12. Generalizable engineering principles

Several principles apply well beyond configuration materialization.

1. **Optimize the amount of work before optimizing the speed of work.** Better algorithms, faster serialization, or increased parallelism cannot fully compensate for unnecessary computation.

2. **Model the affected state explicitly.** The ability to identify change scope is itself a performance capability.

3. **Treat invalidation as a correctness problem.** Updating too much wastes resources; updating too little produces stale state.

4. **Separate planning, scheduling, and execution.** Each layer solves a different problem and can evolve independently.

5. **Make the smallest safe change, not merely the smallest possible change.** When dependencies are uncertain, conservative expansion is preferable to silently missing updates.

6. **Treat state freshness and event ordering as separate concerns.** An ordered event stream does not automatically guarantee that a read replica has observed the relevant database state.

7. **Reduce long-running outliers before adding concurrency.** Expensive outliers can damage queue health, memory stability, recovery behavior, and tail latency.

8. **Preserve full recomputation as a correctness reference.** Even when incremental execution is the default, a full rebuild remains valuable for reconciliation, testing, and exceptional changes.

The central architectural shift is:

```text
OLD MODEL

          Change
             |
             v
   Recompute Everything
             |
             v
   Discover What Changed


NEW MODEL

          Change
             |
             v
  Understand What Changed
             |
             v
 Determine Affected State
             |
             v
Recompute Only What Is Safe
             |
             v
  Verify Resulting State
```

**The most valuable lesson is that incremental computation is not primarily a faster implementation of full computation. It is a different correctness architecture.**

The performance benefits come from reducing the amount of work, while the engineering difficulty shifts toward dependency analysis, state invalidation, concurrency control, and reliable reconciliation.
