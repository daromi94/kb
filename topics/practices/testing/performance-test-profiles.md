# Performance test profiles

Each performance test profile applies a distinct load shape to expose
a different class of failure. One run cannot answer every question,
so validating a system means picking the profiles that match the
risks that matter and running them as separate tests.

## The profiles

| Profile    | Load shape                   | Reveals                      |
|------------|------------------------------|------------------------------|
| Load       | Smooth ramp, hold at target  | SLO compliance, baseline     |
| Stress     | Stepped ramp past the limit  | Breaking point, failure mode |
| Spike      | Instant surge                | Elasticity and load shedding |
| Soak       | Moderate, sustained for days | Leaks and GC drift           |
| Volume     | Static load, large dataset   | Data-size scaling defects    |
| Breakpoint | Steep linear ramp to halt    | Per-component tuning limits  |

## Load test

Ramp smoothly to the anticipated peak concurrency and hold. The goal
is to verify that throughput, latency, and error rate meet the SLOs
under normal operating conditions, and to capture baseline CPU,
memory, and network utilization against which later runs compare.

This profile confirms that current capacity is adequate for daily
traffic. It does not exercise failure modes — by construction, the
load stays inside the envelope.

## Stress test

Step the load up past the anticipated ceiling until something breaks.
The number is not the point; the identity and shape of the failure
are. Which resource ran out — connection pool, thread pool, network
bandwidth? How did the system degrade — graceful rejection or
cascading failure? Did it recover once the load was removed?

A system that fails a stress test loudly is fine. A system that
hides its failure mode until production is not.

## Spike test

Inject a sudden, massive surge in a very short window. Models a
viral event, a flash sale, or a thundering herd from a synchronized
restart. The gradual ramp of a stress test gives autoscalers and
rate limiters time to react; a spike does not.

Spike tests answer whether load balancers and autoscaling groups
respond in time, whether queue management absorbs the shock, whether
load shedding engages, and whether the explosive concurrency exposes
race conditions invisible at lower rates.

## Soak test

Hold a moderate load — typically 70-80% of capacity — for hours or
days. Short tests cannot surface defects that accumulate over time:
memory leaks that eventually trigger out-of-memory, unclosed file
descriptors, leaked database cursors, thread-local buildup, and the
cumulative impact of major garbage collection cycles.

The load level matters less than the duration. Anything strenuous
enough to keep the system continuously working will eventually
expose what slowly decays.

## Volume test

Decouple concurrency from data size. Hold the user load constant
and populate databases, queues, and storage with an enormous corpus
of historical data. The question is whether the data path scales
with the corpus, not with the user count.

This profile reveals missing indexes, joins that degrade with row
count, serialization that allocates per-row, and caching strategies
that collapse once the working set exceeds RAM.

## Breakpoint test

A variant of stress testing: apply a continuous, steep linear ramp
until a critical alert fires or the component halts. The profile
maps the tuning limits of individual components — a specific
microservice, a third-party API, a database — in isolation, before
integration hides which component is the bottleneck.

The output is a per-component capacity number, not a system-level
verdict. Use it during tuning, not as a release gate.

## Related

- [Performance testing](performance-testing.md) - The four choices behind a useful run
- [Saturation curve](saturation-curve.md) - The curve stress and breakpoint tests trace

---

Return to [Testing](_index.md)
