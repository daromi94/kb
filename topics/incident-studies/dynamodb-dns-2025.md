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

## Why recovery failed

Recovery required the next enactor apply cycle to succeed. It did
not: the enactor's write path could not produce a new record while
the prior reference was unresolvable. The state persisted until
operators intervened.

The same terminal state is reachable without a race — deleting the
endpoint record directly produces it. Any dangling reference
triggers the same non-recovery.

## Lessons

Four properties of the system combined to produce the outage.

**Shared-code redundancy.** Three AZ-isolated enactors run identical
logic. AZ isolation protects against infrastructure faults, not code
faults — inputs that stop one stop all three. Surviving this class
of failure requires diverse implementations or graceful-degradation
paths, not replication.

**Transactional serialization across apply operations.** The locking
mechanism produces head-of-line blocking: a stalled enactor delays
its own apply until its plan is generations obsolete. Serialization
primitives meant to prevent concurrent-write anomalies bound
progress on the slowest holder. Where ordering can be reconstructed
from monotonic versions, last-write-wins avoids this failure class.

**Hard failure on missing prior state.** The write path aborts when
its read of the current plan reference is unresolvable, rather than
treating it as "no current plan." In a foundational service, a
dangling reference is a state that will be encountered — treating
it as exceptional turns transient bad state into persistent outage.

**Overlapping cleanup and apply windows.** A plan eligible for
garbage collection can still be the target of an in-flight apply;
the apply step has no pre-write check against the deletion
threshold. Lifecycle bounds enforced only at cleanup permit writes
that are invalid the moment they land — every mutating endpoint
must honor the bound.

---

Return to [Incident studies](_index.md)
