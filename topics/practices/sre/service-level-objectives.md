# Service level objectives

An SLO is a target reliability level for a service, expressed as a
measurable threshold over a defined window. It sits between the SLI
(Service Level Indicator), which is the actual metric being measured,
and the SLA (Service Level Agreement), which is the contractual promise
with financial or legal consequences. SLOs are internal engineering
targets — stricter than SLAs, looser than perfection.

## Anatomy of an SLO

A well-formed SLO has three components:

| Component   | Role                            | Example               |
|-------------|---------------------------------|-----------------------|
| SLI         | What is measured                | Good requests / total |
| Target      | The threshold                   | 99.9%                 |
| Time window | Period over which it's measured | Rolling 28 days       |

The precision of the SLI definition matters enormously. "Successful
request" needs an exact definition — which status codes count as
failures, whether client errors (4xx) are excluded, how timeouts are
classified, whether health-check traffic is filtered out. Ambiguity in
the SLI definition is the most common source of SLO dysfunction because
it makes the number unfalsifiable and politically negotiable after the
fact.

## Choosing good SLIs

The strongest SLIs measure from the user's perspective rather than from
internal system state. Request success rate and latency measured at
the load balancer or API gateway reflect what clients actually
experience. CPU utilization, queue depth, and cache hit ratio are useful
operational metrics but make poor SLIs — a service can have healthy
CPU and sick users simultaneously.

Canonical SLI categories by service type:

| Service type    | SLI categories                               |
|-----------------|----------------------------------------------|
| Request-driven  | Availability, latency, correctness           |
| Data pipelines  | Freshness, coverage, correctness, throughput |
| Storage systems | Durability, availability, latency            |

Latency SLIs should be expressed as percentile thresholds, not
averages. "99% of requests complete in under 300ms" is meaningful;
"average latency under 300ms" hides the tail entirely, and the tail
is where users suffer.

## Common pitfalls

**Target too high.** A 99.999% SLO on a service whose upstream
dependencies offer 99.9% is arithmetically impossible. Targets should
be grounded in historical performance and user requirements, not
aspirational round numbers.

**Measuring the wrong thing.** An SLO on server-side response time that
excludes network and client rendering says nothing about user
experience. Measure as close to the user as the architecture allows.

**Treating the SLO as a ceiling.** If a service consistently exceeds
its target by a wide margin, users come to depend on the higher
reliability and the stated SLO becomes meaningless. Occasionally using
the error budget — through controlled chaos, intentional load-shedding,
or deferring reliability work — keeps the SLO honest and prevents
hidden coupling to over-delivered reliability.

**No consequences.** If budget exhaustion does not change team
behavior — does not pause launches, does not redirect work — the
framework collapses into a dashboard nobody reads.

## Related

- [Error budgets](error-budgets.md) - Operationalizing SLO targets

---

Return to [SRE](_index.md)
