# Log data model

OpenTelemetry defines a structured log data model designed for
machine processing. It standardizes log records across frameworks
and languages.

## Record fields

| Field                | Description                            |
|----------------------|----------------------------------------|
| Timestamp            | When the event occurred                |
| ObservedTimestamp    | When the collector received the record |
| SeverityText         | Human-readable level (INFO, ERROR)     |
| SeverityNumber       | Numeric severity for range filtering   |
| Body                 | The log message                        |
| Attributes           | Structured key-value metadata          |
| TraceId, SpanId      | Correlation to the active trace        |
| TraceFlags           | Sampling state of the correlated trace |
| Resource             | Source of the log                      |
| InstrumentationScope | Scope that emitted the record          |

**SeverityNumber** is a 1-24 numeric scale that enables filtering by
severity range rather than string matching. It maps to conventional
levels (DEBUG, INFO, WARN, ERROR) but with finer granularity.

**ObservedTimestamp** is set by the collection system. It serves as a
fallback when the origin timestamp is unavailable.

## Log correlation

The TraceId, SpanId, and TraceFlags fields link log records to the
active trace. When a log is emitted while a span is active, these
fields are attached automatically, aligning the log entry with the
distributed trace it belongs to.

## Java integration

Application code uses standard logging frameworks (SLF4J, Log4j2,
Logback). The Java agent provides two separate instrumentations:

- **MDC population:** Injects `trace_id`, `span_id`, and
  `trace_flags` into the framework's Mapped Diagnostic Context.
  This makes trace correlation available in existing log patterns
  and sinks without changing the log pipeline.
- **Log appender bridging:** Installs appenders that forward log
  records to the OTel Log SDK, mapping them to the OTel Log Data
  Model for export via OTLP.

Application code rarely interacts with the Logger interface
(`io.opentelemetry.api.logs.Logger`) directly.

---

Return to [OpenTelemetry](_index.md)
