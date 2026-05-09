# Metric instruments

OpenTelemetry defines seven instrument types, split by synchronous
(recorded inline with application code) and asynchronous (reported
via callback when the SDK collects).

## Instrument types

| Instrument               | Sync | Behavior                             |
|--------------------------|------|--------------------------------------|
| Counter                  | Yes  | Monotonically increasing             |
| UpDownCounter            | Yes  | Increases or decreases               |
| Histogram                | Yes  | Distribution across buckets          |
| Gauge                    | Yes  | Current value, set explicitly        |
| Observable Counter       | No   | Monotonic, reported via callback     |
| Observable UpDownCounter | No   | Bidirectional, reported via callback |
| Observable Gauge         | No   | Current value, reported via callback |

**Counter** fits anything that only goes up: requests served, bytes
sent, errors encountered.

**UpDownCounter** fits values that fluctuate: active connections,
queue depth, thread pool size.

**Histogram** records a distribution. The SDK buckets values
automatically. Use it for latencies, payload sizes, or any
measurement where percentiles matter.

**Gauge** records a point-in-time value. The synchronous variant is
set explicitly by application code; the observable variant registers
a callback that the SDK invokes at collection time. Observable
gauges suit values read from external state, like JVM heap usage.

Instruments are created via the Meter
(`io.opentelemetry.api.metrics.Meter`).

## Cardinality

Metrics are aggregated by unique attribute combinations. Each unique
combination produces a separate time series. High cardinality — too
many unique combinations — causes memory pressure in both the SDK
and the backend. Avoid unbounded attribute values like user IDs or
request paths with path parameters.

## Exemplars

Exemplars bridge metrics and traces. When the SDK records a
measurement, it can sample that data point and attach the current
Trace ID and Span ID. The backend stores this alongside the
aggregated metric, enabling direct navigation from a latency spike
to the specific trace that caused it.

---

Return to [OpenTelemetry](_index.md)
