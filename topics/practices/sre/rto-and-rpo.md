# RTO and RPO

RTO (Recovery Time Objective) and RPO (Recovery Point Objective) are
the two foundational metrics of disaster recovery planning. RTO sets
the maximum acceptable downtime. RPO sets the maximum acceptable data
loss. Both are business decisions — determined by consequences (lost
revenue, contractual penalties, regulatory exposure), not by what the
infrastructure happens to support.

## RTO: time to restore service

RTO is the maximum acceptable duration between the moment a disaster
occurs and the moment service is fully restored. A payment processor
measures RTO in minutes. A consumer photo-sharing app might tolerate
24 hours.

The RTO clock includes everything: detection, decision-making,
failover execution, data validation, DNS propagation, cache warming,
and health verification. Teams that only measure the mechanical
failover time underestimate real RTO by a large factor. The human
steps — paging the right people, confirming the incident, getting
authorization to execute destructive recovery actions — often dominate
the timeline.

## RPO: acceptable data loss

RPO is the maximum acceptable amount of data loss, measured as a time
interval. An RPO of 15 minutes means the recovered system may be
missing up to 15 minutes of the most recent writes. An RPO of zero
means every committed write must survive.

RPO is determined by the gap between the last durable copy and the
moment of failure:

| Replication method | Typical RPO        | Tradeoff            |
|--------------------|--------------------|---------------------|
| Periodic backups   | Hours              | Cheap, large gap    |
| Async replication  | Seconds to minutes | Lag can balloon     |
| Sync replication   | Near zero          | Write latency floor |

A financial ledger demands RPO of zero. A logging system might accept
hours. The right number depends on the cost of losing that data, not
on what is technically convenient.

## Relationship and cost curve

RTO and RPO are independent dimensions. A system can have aggressive
RPO and relaxed RTO (no data loss tolerated, but acceptable to be
down for a day while restoring), or the inverse (fast failover, but
some recent writes may be lost).

Tightening either number costs money, and the cost curve is steeply
nonlinear. Moving RPO from one hour to one minute means replacing
nightly backups with continuous log shipping. Moving from one minute
to zero means synchronous cross-region replication — a latency floor
on every write and infrastructure in at least two failure domains.
Moving RTO from hours to seconds means a hot standby that is always
running and always ready, effectively doubling the infrastructure
footprint.

## Pitfalls

**Untested targets.** A documented four-hour RTO that has never been
exercised is a hope, not a plan. Regular game days and failover drills
are the only way to validate the numbers under real conditions, with
real people and real pressure.

**Happy-path measurement only.** Clean, announced failovers are the
easy case. Partial failures, corruption that replicates before
detection, and simultaneous loss of primary and backup are harder.
Synchronous replication faithfully copies corruption to every replica,
making the RPO calculation misleading. Point-in-time recovery — the
ability to restore to a moment before the corruption — is a separate
capability that pure replication does not provide.

**Uniform targets.** The authentication service and the recommendation
engine do not need the same recovery guarantees. Spending to give a
non-critical service a one-minute RTO is waste that could have funded
better protection elsewhere.

**Circular dependencies.** Runbooks stored only in the failed region,
credentials locked in a vault that requires the down service to
access, on-call rotations managed by a tool hosted on the affected
infrastructure — these turn a four-hour RTO into a four-day outage.

---

Return to [SRE](_index.md)
