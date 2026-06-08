# Three pillars of observability

Metrics, logs, and traces are the three signals a system emits, and
each answers a different question. Metrics tell you how much, logs
tell you what, and traces tell you where. Only traces follow a single
request across service boundaries, so they supply the cross-service
context that metrics and logs lack.

| Pillar  | Question | Scope                        |
|---------|----------|------------------------------|
| Metrics | How much | Aggregate over time          |
| Logs    | What     | One event, one component     |
| Traces  | Where    | One request, across services |

## Metrics

A metric is a numeric value aggregated over an interval of time. Metrics
are cheap to store and ideal for baselines and alerts: one shows that
p99 latency jumped from 50 ms to 800 ms, or that an error budget is
burning too fast. Aggregation is also their limit. By collapsing many
requests into a single number, a metric reports that a problem exists
but discards the per-request detail needed to explain why.

## Logs

A log is a discrete, timestamped record of an event, carrying
high-fidelity detail such as a stack trace or an out-of-memory error.
Each line is localized: on its own it records what happened in one place
with no built-in link to the request that triggered it elsewhere.
Correlating log lines across services therefore requires a shared
correlation ID that you add deliberately.

## Traces

A trace records the lifecycle of one request as it crosses multiple
service boundaries.

**Span:** a single unit of work within a trace, such as one service
handling the request or one database query. A trace is a tree of spans.

Context propagation links spans into one trace: each service injects a
trace context into the metadata of its outbound network calls, and the
next service extracts it. The wire standard for this is W3C Trace
Context, which defines the `traceparent` and `tracestate` headers so a
trace holds together across tools from different vendors.

---

Return to [Observability](_index.md)
