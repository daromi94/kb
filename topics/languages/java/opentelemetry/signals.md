# Signals

OpenTelemetry organizes observability data into three signal types:
traces, metrics, and logs.

## Traces and spans

A Trace represents the full journey of a single request across a
system. It is composed of Spans — each Span represents one operation
within that journey (e.g., authenticating a user, querying a database).

Every Span carries:

- A name
- A start and end timestamp
- A unique Span ID
- The shared Trace ID of the parent trace
- Attributes, events, links, status, and Span kind

All Spans in a trace share the same Trace ID.

## Metrics

Metrics are numerical measurements aggregated over time. Unlike traces,
which are request-scoped, metrics capture system-level state: CPU usage,
thread pool sizes, error counters.

## Logs

Logs are timestamped event records — the same data produced by SLF4J,
Logback, or Log4j2.

**Log correlation** links logs to traces by injecting the current Trace
ID and Span ID into log output. With the Java agent, this happens
automatically via MDC population. With the SDK alone, you must install
a logging bridge (e.g., the Logback MDC shim) and update your log
pattern to include the MDC keys.

---

Return to [OpenTelemetry](_index.md)
