# Error budgets

An error budget is the amount of unreliability a service is allowed
before it breaches its SLO. If the target is 99.9% over a rolling
28-day window, the budget is the remaining 0.1% — roughly 40 minutes
of total downtime, or about 40,000 failed requests out of 40 million
served. The budget is not a failure threshold to fear. It is a
resource to spend.

## Reliability versus velocity

Product teams want to ship fast. Operations teams want stability.
Without a shared framework, every launch becomes a political argument
about whether the risk is acceptable.

The error budget resolves this by making reliability fungible. When
the budget is healthy, teams ship aggressively — push changes faster,
run experiments, take calculated risks. When the budget is exhausted
or burning too fast, the team shifts to stabilization: freeze risky
launches, prioritize reliability work, pay down incident debt. The
decision of whether to ship is no longer a judgment call. It is a
reading on a gauge.

## Burn rate alerting

Alerting on a raw SLO breach after the fact is useless — by the time
a 28-day target is violated, the incident happened days ago. The
practical approach is to alert on the rate at which the budget is
being consumed.

**Burn rate** measures how fast the budget is draining relative to its
natural pace. A burn rate of 1 means the budget is being consumed at
exactly the pace that would exhaust it by the end of the window — no
faster, no slower. A burn rate of 14.4 means it is draining 14.4
times faster than sustainable.

Two alert tiers cover different failure modes:

| Alert tier | Burn rate | Window | Budget consumed | Catches                 |
|------------|-----------|--------|-----------------|-------------------------|
| Fast burn  | 14.4      | 1h     | ~2%             | Sharp, sudden incidents |
| Slow burn  | 6         | 6h     | ~5%             | Sustained degradation   |

Each tier pairs two windows. The detection window identifies the
trend over a longer period. The confirmation window requires the
problem to persist for a shorter minimum duration before firing.
This prevents paging on transient blips while still catching real
incidents quickly.

---

Return to [SRE](_index.md)
