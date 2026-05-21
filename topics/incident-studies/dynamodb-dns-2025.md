# AWS DynamoDB DNS outage (Oct 2025)

A race in DynamoDB's DNS routing automation left the US-EAST-1
regional endpoint resolving to no IP addresses. The routing system
could not self-heal, so the outage ran 14.5 hours and ended only
when operators intervened.

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

## The routing system

DynamoDB's regional endpoint is published through Route 53. Two
components keep its DNS record up-to-date:

- **Planner:** A single process that produces numbered routing
  plans from load measurements.
- **DNS Enactor:** A process that polls for new plans, applies them
  to Route 53, and garbage-collects stale plans. It runs as three
  independent instances, one per Availability Zone.

```text
+-----------+
| Planner   |
| generates |
| Plan N    |
+-----+-----+
      |
      v
+-----+---------+
| DNS Enactor   |
| (one per AZ)  |
| applies plan  |
| GCs old plans |
+-----+---------+
      |
      v
+-----+--------+
| Route 53     |
| endpoint DNS |
+--------------+
```

## Failure sequence

1. One enactor stalled while applying a plan. The other enactors
   continued applying newer plans.
2. The stalled enactor's check for stale plans did not reject its
   plan — the delay had made the timestamp comparison unreliable —
   so it overwrote the regional endpoint with that now-obsolete
   plan.
3. Another enactor's garbage collector deleted that same plan,
   already many generations behind.
4. The regional endpoint referenced a deleted plan and resolved
   to no IP addresses.

## Lessons

**A late write must not overwrite newer state.** Order writes by a
sequence number, not a timestamp, so a late write is dropped, not
applied.

**A one-sided invariant does not hold.** If cleanup deletes data
past an age limit, no writer may reference data past that limit.

**A recovery path must run from the broken state.** If every write
must first read valid current state, nothing can fix a broken one.
Let writes proceed even when the current state cannot be read, so
they can overwrite it.

---

Return to [Incident studies](_index.md)
