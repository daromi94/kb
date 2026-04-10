# Load test types

Performance tests target distinct failure modes. Each type varies in
load profile, duration, and what it reveals.

## Load test

Sustain expected peak traffic to verify the system holds its SLOs.
Measure in requests per second, response time percentiles, or
concurrent users — pick the metric that maps to your SLIs.

Two variants. Browsing tests hit multiple endpoints with varied
parameters and may or may not include the caching layer.
Transactional tests execute multi-step workflows (authentication,
query, write) where each request depends on the previous one — these
require per-transaction latency tracking.

## Stress test

Push beyond expected peak to find the breaking point. The output is
the failure mode itself — does the system shed load, degrade
gracefully, or cascade into total failure? Ramp in steps past the
expected ceiling, holding each step long enough for metrics to
stabilize.

## Soak test

Sustain moderate load for hours or days. Targets defects that only
surface over time: memory leaks, connection leaks, log disk
exhaustion, cache degradation, and slow resource accumulation that
short runs miss. Use a constant request rate and measure degradation
by latency drift and error rate, not achieved throughput. Distributed
tracing with correlation IDs isolates per-component bottlenecks.

## Spike test

Inject a massive instantaneous burst to evaluate auto-scaling, load
shedding, and circuit breakers under sudden demand. The question is
whether the system absorbs the burst without cascading failure and
recovers to baseline once the spike subsides.

## Capacity test

Gradually ramp to determine maximum sustainable throughput. Differs
from a stress test in focus: stress tests observe failure modes,
capacity tests find the ceiling. The result feeds directly into
capacity planning and scaling policy decisions.

## Supplementary

### Auto-scaling validation

Verify that elasticity triggers fire and settle correctly under
stepped load increases. Start with more than one instance — scaling
from a single instance has limited headroom. Monitor both scale-up
and scale-down events and confirm that new capacity does not
immediately trigger further scaling cascades.

### Functionality check

Reuse existing load test scenarios at low volume against production
during off-peak hours. Acts as a synthetic monitoring layer that
catches functional regressions under realistic multi-step request
patterns.

## Summary

| Type     | Goal                  | Load level      | Duration        |
|----------|-----------------------|-----------------|-----------------|
| Load     | Verify SLO compliance | Expected peak   | Sustained       |
| Stress   | Find breaking point   | Beyond expected | Stepped ramp    |
| Soak     | Expose resource leaks | Moderate steady | Hours to days   |
| Spike    | Test burst resilience | Sudden massive  | Minutes         |
| Capacity | Find max throughput   | Gradual ramp    | Until saturated |

## Related

- [Load test planning](load-test-planning.md) - Objectives and methodology

---

Return to [Testing](_index.md)
