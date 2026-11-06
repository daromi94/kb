# Safe unplanned failover

Unplanned failover is fundamentally a problem of making irreversible decisions under incomplete information.

When the primary node of a replicated system becomes unreachable, two questions arise:

1. Is the primary actually dead, or merely unreachable?
2. Which replica can safely become the new primary without losing committed data?

The difficulty is that these questions are not independent. A system can select the replica containing the most recent data and still create a split-brain situation if the old primary remains active.

A reliable failover protocol must therefore solve three distinct problems:

- Failure detection: Determine whether recovery is necessary.
- Fencing: Prevent the old primary from continuing to commit writes.
- State recovery: Select a replacement that preserves as much committed history as possible.

The central design principle is:

**Failover is not simply promoting a healthy replica. It is a coordinated transition of write authority and durable state.**

## 1. The problem: failure is indistinguishable from unreachability

Consider a replicated database with one primary, three replicas, and a control plane responsible for monitoring the cluster.

```text
             Control Plane
                   |
                   v
             Health Checks
                   |
                   v
             +-----------+
             | Primary P |
             +-----------+
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
+----+          +----+          +----+
| R1 |          | R2 |          | R3 |
+----+          +----+          +----+

            WAL Replication
```

The primary accepts writes. Replicas continuously receive and replay the primary's write-ahead log (WAL).

Now suppose the control plane loses connectivity to P.

```text
             Control Plane
                   |
                   X
                   |
             +-----------+
             | Primary P |
             +-----------+
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
+----+          +----+          +----+
| R1 |          | R2 |          | R3 |
+----+          +----+          +----+
```

There are multiple possible explanations:

- P crashed.
- The host running P lost network connectivity.
- The control plane became isolated from P.
- P is running but its database process is frozen.
- P remains healthy and is still serving applications and replicas.

The control plane cannot distinguish these possibilities from its own failed connection.

This is a fundamental property of asynchronous distributed systems: **a timeout is evidence of unresponsiveness, not proof of failure.**

Increasing the number of retries does not solve the problem. A network partition can last indefinitely.

### The dangerous approach: immediate promotion

```text
              Control Plane
                    |
                    v
               P timed out
                    |
                    v
               Promote R1
                    |
      +-------------+-------------+
      |                           |
      v                           v
+----------+                +----------+
|  Old P   |                |  New R1  |
| WRITABLE |                | WRITABLE |
+----------+                +----------+

               SPLIT BRAIN
```

If the old primary is still accepting writes, two independent histories can emerge.

Once this happens, restoring a single consistent history may require discarding or reconciling writes.

**Therefore, failure detection must be separated from the authorization to fail over.**

## 2. Distributed observations: use the replicas as witnesses

Instead of trusting only its own health check, the control plane can ask the replicas whether they are still receiving updates from the primary.

This produces information from multiple network perspectives.

```text
             Control Plane
                   |
   +---------------+---------------+
   |               |               |
   v               v               v
+----+          +----+          +----+
| R1 |          | R2 |          | R3 |
+----+          +----+          +----+
   |               |               |
   +---------------+---------------+
                   |
                   v
          Replication status
                   |
                   v
            Decision logic
```

Consider three scenarios.

| Observation                                                                 | Interpretation                                | Decision                                 |
| --------------------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------- |
| Control plane cannot reach P, but R1 is still replicating                   | P may be healthy                              | Do not promote                           |
| Control plane cannot reach P; reachable replicas report replication failure | Evidence supports primary unavailability      | Begin recovery, subject to safety checks |
| Control plane cannot reach P or any replica                                 | Insufficient evidence and no promotion target | Wait                                     |

The important insight is that replication health provides stronger operational evidence than isolated node health checks.

However, an important limitation remains.

Suppose R1 and R2 report failed replication, but R3 is unreachable from the control plane.

R3 might still be receiving updates from P.

Therefore, **agreement among reachable replicas does not necessarily establish agreement among all replicas.**

This distinction becomes critical when examining the replication durability contract.

## 3. Use the durability protocol to constrain the old primary

This is one of the most interesting architectural techniques.

Instead of relying solely on a failure detector, the system can exploit its replication protocol to limit what an isolated primary is allowed to commit.

### Synchronous replication

Consider a configuration in which every transaction must be durably acknowledged by at least one replica before the primary can acknowledge success to the client.

Conceptually:

```text
              Client
                 |
                 v
              COMMIT
                 |
                 v
              Primary
                 |
                 v
            WAL record
                 |
 +---------------+---------------+
 |               |               |
 v               v               v
R1              R2              R3
 |
 +---- ACK ----->+
                 |
                 v
          Client success
```

Only one eligible replica needs to acknowledge the transaction.

A quorum-style synchronous standby configuration can express this as:

```conf
synchronous_standby_names = 'ANY 1 (R1, R2, R3)'
synchronous_commit = on
```

Here, an acknowledgement requires the WAL to be flushed durably on an eligible standby, not necessarily replayed into query-visible state.

Now imagine P loses connectivity to every eligible replica.

```text
             Primary P
                 |
                 v
             WAL write
                 |
 +---------------+---------------+
 X               X               X
 |               |               |
R1              R2              R3

        No synchronous ACK
                 |
                 v
           COMMIT cannot
          be acknowledged
```

Under this configuration, P cannot successfully acknowledge new synchronous commits.

The primary might still be running, but it is no longer capable of completing the normal write protocol.

This changes the recovery question from:

Is the old primary dead?

to:

Can the old primary still successfully commit transactions?

The second question is often more useful because it is directly connected to the safety requirement.

### But there is a subtle problem

Suppose the control plane can communicate with R1 and R2, while P and R3 are isolated together.

```text
     Control Plane
           |
 +---------+---------+
 |                   |
 v                   v
R1                  R2
 X                   X
 |                   |
 +---------X---------+
           |
   Network Partition
           |
     +-----------+
     | Primary P |
     +-----------+
           |
           v
          R3
           |
          ACK
```

P can still commit through R3.

If the control plane promotes R1, two writable primaries may coexist.

**The key limitation is that `ANY 1` provides a durability acknowledgement rule, not a consensus-based leadership protocol.**

A reachable subset reporting failed replication is therefore an operational recovery signal, not a mathematical proof that the primary has lost write authority.

This introduces a major trade-off:

| More aggressive failover            | More conservative failover    |
| ----------------------------------- | ----------------------------- |
| Faster recovery                     | Potentially longer outages    |
| Tolerates more uncertainty          | Requires stronger evidence    |
| Greater risk of conflicting writers | Stronger safety               |
| Better apparent availability        | More likely to defer recovery |

For strict single-writer guarantees, additional mechanisms may be needed: fencing, leases, leadership epochs, or a consensus-backed authority.

The general principle is to **make the conditions for successful writes incompatible with conflicting leadership, rather than merely hoping that the previous leader has stopped.**

## 4. Failure detection must cover the entire protocol stack

A distributed failure detector must handle different kinds of failures.

Not all failures are visible at the same layer.

### Case A: Process crash

The database process exits.

A local supervisor can detect the exit immediately and notify the control plane.

The control plane still needs to corroborate the failure before making a leadership decision.

### Case B: Network rejection

Connections fail explicitly because of a firewall, routing error, or actively rejected connection.

Detection can be fast because the networking layer returns an error.

### Case C: Silent packet loss

Packets disappear, but existing connections may remain apparently established.

This is more difficult.

TCP keepalives and `TCP_USER_TIMEOUT` can help detect dead transport connections.

### Case D: Frozen application

The application is unresponsive, but the kernel continues to handle TCP traffic.

```text
  Replica R1
       |
       v
TCP connection
       |
       v
+-------------+
| Kernel      |  ACTIVE
+-------------+
       |
       v
+-------------+
| Database    |  FROZEN
| Process     |
+-------------+
```

**Transport-level health does not imply application-level progress.**

An application-level replication timeout is needed to detect that replication has stopped making progress.

For PostgreSQL, `wal_receiver_timeout` terminates inactive replication connections.

### Engineering lesson: normalize failures into a common signal

Rather than building a separate recovery algorithm for each failure type, configure the system so that different failures eventually produce a common observation:

```text
Process crash --------+
                      |
Network rejection ----+
                      |
Silent packet loss ---+----> Replication broken
                      |              |
Frozen process -------+              v
                              Recovery logic
```

This reduces complexity in the recovery state machine.

The tuning trade-off remains important:

- Short timeouts reduce failure detection time but increase false suspicions during stalls or congestion.
- Long timeouts reduce false suspicions but increase recovery latency.

A useful decomposition is:

```text
Recovery time =
    detection
  + confirmation
  + fencing
  + candidate selection
  + promotion
  + routing convergence
  + replication readiness
```

Optimizing only the failure detector does not necessarily optimize total recovery time.

## 5. Fencing: prevent the old primary from returning unexpectedly

Suppose the control plane decides to promote a replica.

Before promotion, the old primary might recover.

This creates a dangerous race.

```text
Time
 |                  P becomes unreachable
 |                            |
 |                            v
 |             Control plane suspects failure
 |                            |
 |                            v
 |                Control plane selects R2
 |                            |
 |                            +----------------------------------+
 |                            |                                  |
 |                            v                                  v
 |                       Promote R2                         P recovers
 |                            |                                  |
 |                            |                        P resumes replication
 |                            |                                  |
 |                            +----------------X-----------------+
 v                                         CONFLICT
```

A robust protocol needs a point beyond which the old primary must not regain write authority.

One technique is to deliberately disconnect replicas from the old primary before selecting a new leader.

```text
BEFORE FENCING

           Primary P
               |
   +-----------+-----------+
   |           |           |
   v           v           v
  R1          R2          R3


AFTER DISCONNECTION

           Primary P
               |
   +-----------+-----------+
   X           X           X
   |           |           |
  R1          R2          R3
```

This achieves two things simultaneously.

First, it prevents a returning primary from obtaining synchronous acknowledgements from those disconnected replicas.

Second, it freezes replication progress, allowing the control plane to compare stable WAL positions.

The same operation therefore contributes to both safety and recovery.

But this is conditional fencing. It only prevents commits if the old primary has no other eligible replica through which it can obtain acknowledgements, and the synchronous durability policy remains enforced.

**It does not protect against an unreachable eligible replica still connected to the old primary.**

For a stronger guarantee, the system needs authoritative fencing that does not depend on every replica being reachable.

Examples include revoking an exclusive lease, enforcing a monotonically increasing leadership epoch at the write path, or isolating the old primary at an infrastructure layer.

**Generalizable pattern: Before transferring ownership, make the previous owner incapable of performing conflicting operations.**

This applies to distributed databases, storage controllers, schedulers, and singleton workers.

## 6. Choosing a replacement: durable state matters more than node health

Once the old primary is fenced as far as the protocol can guarantee, the next problem is selecting a replacement.

Replicas may have received different amounts of WAL.

Consider:

```text
Replica       Received WAL      Replayed WAL
------------------------------------------------
R1                120               120
R2                125               122
R3                123               123
```

The distinction matters:

- Received: WAL has arrived at the replica; for durability decisions, the relevant boundary is the durably flushed WAL position.
- Replayed: WAL has actually been applied to the local database state.

R3 has replayed more than R2, but R2 has received more WAL overall.

Which replica should become primary?

### Prefer the replica with the most complete durable history

WAL is sequential.

Under a common replication timeline:

```text
R1: [================120]

R2: [=====================125]
                           ^
                  latest durable WAL

R3: [===================123]
```

A replica containing the durable WAL prefix through position 125 also contains earlier WAL records.

Therefore, R2 is the strongest recovery candidate, assuming its WAL is valid, its timeline is compatible, and it can be promoted.

Selecting R3 merely because it has replayed further would unnecessarily discard WAL already present on R2.

The recovery controller can wait briefly for R2 to replay its locally stored WAL, then promote it.

This illustrates an important distinction:

**Replication progress and execution progress are not the same thing.**

WAL reception preserves information. WAL replay materializes that information into database state.

### Why this works with rotating synchronous acknowledgements

Suppose synchronous acknowledgements were provided by different replicas over time.

```text
Committed WAL position    Acknowledging replica
------------------------------------------------
100                       R1
110                       R3
120                       R1
125                       R2
```

Because the log is sequential, R2 having a complete durable prefix through 125 means it also has the WAL preceding 125.

It is unnecessary to reconstruct which replica acknowledged every individual transaction.

Instead, a candidate with the greatest complete durable prefix can preserve all acknowledged transactions represented in that surviving history.

This is a powerful consequence of ordered, append-only logs.

### Critical limitation: surviving WAL

If the only copy of an acknowledged WAL record exists on a replica that was lost, another replica cannot magically reconstruct it.

For example:

```text
P:    [=====================125]      LOST
R1:   [================120]           ALIVE
R2:   [=====================125]      LOST
R3:   [==================122]         ALIVE
```

Even with synchronous replication, an acknowledged commit at 125 may be unavailable if P and R2 both lose their durable copies.

**Synchronous replication only provides durability within its failure assumptions. It cannot guarantee survival of arbitrary correlated failures.**

Cross-failure-domain replica placement reduces this risk at the cost of replication latency.

## 7. Promotion is a protocol, not a single command

A correct failover requires multiple coordinated transitions.

```text
+-----------------------+
| Suspect primary       |
+-----------------------+
            |
            v
+-----------------------+
| Validate observations |
+-----------------------+
            |
            v
+-----------------------+
| Isolate old primary   |
| and freeze replicas   |
+-----------------------+
            |
            v
+-----------------------+
| Select WAL candidate  |
+-----------------------+
            |
            v
+-----------------------+
| Promote new primary   |
+-----------------------+
            |
            v
+-----------------------+
| Update write routing  |
+-----------------------+
            |
            v
+-----------------------+
| Reattach replicas     |
+-----------------------+
            |
            v
+-----------------------+
| Resume writes         |
+-----------------------+
```

The ordering is important.

Fencing must precede conflicting write authority. Candidate selection must use a stable understanding of surviving log history. Routing should only direct writes to a primary that is ready to serve them.

The new primary may also need a synchronous standby before it can acknowledge commits.

That means **leadership promotion and write availability are distinct milestones.**

A node can successfully become primary while writes remain blocked because the required replication acknowledgements are not yet possible.

A robust control plane should represent these as separate states.

For example:

```text
     SUSPECTED
         |
         v
RECOVERY_COMMITTED
         |
         v
OLD_PRIMARY_FENCED
         |
         v
CANDIDATE_SELECTED
         |
         v
     PROMOTED
         |
         v
 REPLICATION_READY
         |
         v
     WRITABLE
```

**Every transition should be observable and safe to retry, particularly if the controller crashes partway through the procedure.**

This leads to a further design implication: the control plane itself needs coordination. Multiple controllers must not independently promote conflicting candidates. Durable recovery intent, serialized authority, and monotonically increasing epochs are common ways of addressing this.

## 8. Do not automatically trust the old primary when it returns

An old primary may contain a WAL suffix that does not exist on the new primary.

```text
Old P: [====================A,B]--[C]

New P: [====================A,B]--[D,E]
```

The histories have diverged.

Even if old P has additional WAL records, they cannot automatically be merged into the new history.

Some records may correspond to transactions that were never acknowledged. Some may represent valid transactions from the previous timeline. The system must distinguish these carefully.

An appropriate recovery policy is to quarantine the old primary and prevent it from serving traffic.

Its logs, WAL, and persistent state can be retained for diagnosis.

**Only after reconciliation, rewind, or rebuilding should it be allowed to rejoin as a replica.**

This prevents a transiently failed node from silently restoring obsolete leadership or introducing incompatible state.

### Another subtle consequence: ambiguous commits

A client can lose its connection after a transaction has become durable but before receiving the acknowledgement.

```text
Client                Primary                 Replica
   |                     |                       |
   |------ COMMIT ------>|                       |
   |                     |-------- WAL --------->|
   |                     |<-------- ACK ---------|
   |                     |
   X                     |
   |               Primary fails
   |
   | Client does not know
   | whether commit succeeded
```

**After failover, the transaction may exist on the new primary despite the client observing an error.**

Thus failover also has implications for application correctness. Retried writes should use idempotency keys, uniqueness constraints, or other mechanisms that handle unknown transaction outcomes.

## 9. The fundamental trade-offs

| Design decision                         | Benefit                                                 | Cost or limitation                                          |
| --------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| Ask replicas for failure evidence       | More informative than a single health check             | Reachable replicas may not represent the entire cluster     |
| Short replication timeouts              | Faster detection                                        | Increased sensitivity to transient delays                   |
| Synchronous replication                 | Protects acknowledged writes within failure assumptions | Higher commit latency; writes may block                     |
| Disconnect replicas before promotion    | Stabilizes WAL and constrains old-primary commits       | Does not fence unreachable acknowledgement-capable replicas |
| Choose the highest durable WAL position | Maximizes recoverable history                           | May require replay delay or reconciliation                  |
| Require a standby after promotion       | Maintains durability guarantees                         | Write service can remain unavailable                        |
| Quarantine the old primary              | Prevents accidental reuse of divergent state            | Additional recovery and operational work                    |

**The most important trade-off is between recovery speed and confidence in exclusive write authority.**

A system can make aggressive decisions with incomplete evidence, but this raises the risk of conflicting histories. Conversely, demanding stronger evidence can leave the system unavailable even when surviving replicas are perfectly capable of serving traffic.

## 10. General engineering lessons

Several architectural patterns emerge.

1. **Separate detection from authority.** A failure detector may suspect a failed node, but it should not independently grant leadership.
2. **Use protocol-level evidence.** Replication state and acknowledgement capabilities are more relevant to failover correctness than simple connectivity.
3. **Design fencing into the write path.** Disabling routing alone does not guarantee that the old leader cannot commit.
4. **Stabilize the state before making comparisons.** A recovery candidate must be chosen against a consistent view of surviving log history.
5. **Exploit log structure.** An ordered durable log makes progress comparable and simplifies recovery when histories share a common prefix.
6. **Preserve uncertainty explicitly.** If the system cannot prove enough to recover safely, remaining unavailable can be the correct decision.
7. **Make recovery restartable.** A controller failure during promotion must not create competing leadership decisions.
8. **Treat recovery as a state transition with invariants.** Each stage should establish conditions required by the next stage.

**The deepest lesson is that availability is not simply about restarting failed work; it is about safely transferring authority over shared state.**

The challenging part is often not detecting the failure or starting a replacement. It is ensuring that the replacement is the only node authorized to move the system's history forward.
