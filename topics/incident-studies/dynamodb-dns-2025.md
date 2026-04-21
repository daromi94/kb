# AWS DynamoDB DNS outage (Oct 2025)

A 14.5-hour US-EAST-1 outage in which the DynamoDB regional endpoint
was left resolving to no IP addresses after a race in the DNS
routing automation. Recovery required manual operator intervention
because the enactor processes could not make forward progress from
the resulting state.

## Incident

| Field     | Value                                       |
|-----------|---------------------------------------------|
| Start     | 2025-10-19 23:48 PDT                        |
| End       | 2025-10-20 14:20 PDT                        |
| Duration  | ~14.5 hours                                 |
| Region    | US-EAST-1 only                              |
| Primary   | DynamoDB, EC2, Network Load Balancer        |
| Cascading | Lambda, ECS, EKS, Fargate, STS/IAM, Connect |
| Recovery  | Manual operator intervention                |

EC2 internal subsystems depend on DynamoDB for state, propagating
the failure beyond DynamoDB itself.

## The routing system

DynamoDB regional endpoints are published in Route 53. Two
components manage the automation:

- **Planner:** Single process producing numbered routing plans from
  load measurements.
- **DNS Enactor:** Runs independently in three Availability Zones.
  Each instance polls for new plans, applies them to Route 53 via
  transactions, and garbage-collects plans many generations old.

```
+-----------+
| Planner   |
| generates |
| Plan N    |
+-----------+
      |
      v
+---------------+
| DNS Enactor   |
| (one per AZ)  |
| applies plan  |
| GCs old plans |
+---------------+
      |
      v
+--------------+
| Route 53     |
| endpoint DNS |
+--------------+
```

## Failure sequence

1. One enactor stalled while processing an older plan. Other
   enactors continued applying newer plans.
2. The stalled enactor's stale-plan validity check failed — timestamp
   comparisons became unreliable under the delay — and it overwrote
   the regional endpoint with the much older plan.
3. Another enactor's garbage collector deleted that older plan,
   already many generations behind.
4. The regional endpoint referenced a deleted plan and resolved to
   no IP addresses.
5. Enactor processes reading this state could not apply further
   plan updates. The system remained stuck until operators
   intervened.

## Terminal state

The race produced a specific terminal state: endpoint resolving to
no addresses, referenced plan deleted. The endpoint pointed at a
record that no longer existed.

Recovery from this state required the next enactor apply cycle to
succeed. It did not, because the enactor's write path reads the
current plan reference before computing the next write and aborts
when that reference cannot be resolved. With no successful write
possible, the state persisted until manually corrected.

The same terminal state is reachable without a race — for example,
by deleting the endpoint's DNS record directly. Any input that
leaves a dangling reference triggers the same non-recovery.

## Systemic properties

Four properties of the system combined to produce the outage:

- **Shared-code redundancy.** Three AZ-isolated enactors run
  identical logic. Inputs that stop one stop all three. AZ
  isolation protects against infrastructure faults, not code
  faults.

- **Transactional serialization across apply operations.** The
  locking mechanism produces head-of-line blocking. A stalled
  enactor delays its own apply until the plan it holds is
  generations obsolete.

- **Hard failure on missing prior state.** The write path treats
  an unresolvable current-plan reference as fatal rather than as
  "no current plan." A transient dangling reference becomes a
  persistent outage.

- **Overlapping cleanup and apply windows.** A plan eligible for
  garbage collection can still be the target of an in-flight
  apply. The apply step has no pre-write check against the
  deletion threshold.

Individually, each is a hazard. Together they produce a terminal
state that the normal update loop cannot clear.

## Lessons

**Replicated processes share failure modes.** N instances of the
same code fail on the same inputs. Replication covers
infrastructure faults, not logic faults. Diverse implementations
or graceful degradation paths are required to survive inputs that
cause hard failure.

**Serialization primitives can introduce liveness bugs.** A lock
or transaction intended to prevent concurrent-write anomalies
also bounds progress on the slowest holder. In systems where
ordering can be reconstructed from monotonic versions,
last-write-wins avoids this class of failure.

**Absent prior state is a reachable input on the critical path.**
Write paths that read prior state must treat unresolvable or
missing reads as a valid case, not an exception. In a
foundational service, a dangling reference is a state the system
will encounter.

**Lifecycle invariants must hold at every mutating endpoint.** If
records have a deletion threshold, every write that consumes
those records must honor the same threshold. An invariant
enforced only at cleanup, not at apply, permits writes that are
invalid the moment they land.

---

Return to [Incident studies](_index.md)
