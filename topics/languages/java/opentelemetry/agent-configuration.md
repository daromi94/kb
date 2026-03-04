# Agent configuration

The Java agent accepts configuration through three sources, evaluated
in descending precedence:

1. **System properties** — JVM arguments like
   `-Dotel.service.name=billing-service`.
2. **Environment variables** — Converted from property names by
   uppercasing and replacing dots/dashes with underscores
   (`OTEL_SERVICE_NAME=billing-service`).
3. **Properties file** — Supplied via
   `OTEL_JAVAAGENT_CONFIGURATION_FILE=path/to/config.properties`.

A higher-precedence source always wins when the same key appears at
multiple levels.

## Resource identity

Every instrumented process must declare its identity before telemetry
is exported.

| Env var                    | System property            | Purpose                                                        |
|----------------------------|----------------------------|----------------------------------------------------------------|
| `OTEL_SERVICE_NAME`        | `otel.service.name`        | Logical application name                                       |
| `OTEL_RESOURCE_ATTRIBUTES` | `otel.resource.attributes` | Global key-value pairs on all signals (e.g., `region=us-east`) |

`OTEL_SERVICE_NAME` is the primary query key in most backends. Resource
attributes attach to every span, metric, and log record the process
emits.

## Exporter settings

Telemetry is routed to a destination — typically an OpenTelemetry
Collector. The default protocol is OTLP over HTTP/Protobuf.

| Env var                       | System property               | Purpose                  |
|-------------------------------|-------------------------------|--------------------------|
| `OTEL_TRACES_EXPORTER`        | `otel.traces.exporter`        | Trace destination        |
| `OTEL_METRICS_EXPORTER`       | `otel.metrics.exporter`       | Metric destination       |
| `OTEL_LOGS_EXPORTER`          | `otel.logs.exporter`          | Log destination          |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `otel.exporter.otlp.endpoint` | OTLP target URL          |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `otel.exporter.otlp.protocol` | `http/protobuf` / `grpc` |

Exporter values: `otlp`, `logging` (console), `none`. Traces also
accept `zipkin`; metrics also accept `prometheus`.

## Debugging

When telemetry fails to appear, the agent's internal logging helps
diagnose connectivity or bytecode injection problems.

`-Dotel.javaagent.debug=true` enables verbose output covering class
transformations and exporter network state.

The `otel.javaagent.logging` property controls where agent logs go:

| Value         | Destination                                      |
|---------------|--------------------------------------------------|
| `simple`      | Standard error stream (default)                  |
| `none`        | Suppressed                                       |
| `application` | Routed through the app's SLF4J/Logback framework |

## Related

- [Data pipeline](data-pipeline.md) - Exporters and the Collector
- [Instrumentation tuning](instrumentation-tuning.md) - Module and sampling control

---

Return to [OpenTelemetry](_index.md)
