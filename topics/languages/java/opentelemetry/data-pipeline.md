# Data pipeline

Once the SDK collects telemetry, exporters and the Collector move it
to an observability backend.

## Exporters

Exporters translate telemetry data into a wire protocol. The standard
protocol is OTLP (OpenTelemetry Protocol), which defines encoding,
transport, and delivery semantics. OTLP supports three transport
variants:

| Transport       | Description                 |
|-----------------|-----------------------------|
| `grpc`          | Protobuf over gRPC (HTTP/2) |
| `http/protobuf` | Protobuf over HTTP          |
| `http/json`     | JSON over HTTP              |

If an SDK supports only one transport, it should be `http/protobuf`.

## The collector

The OpenTelemetry Collector is a vendor-agnostic telemetry pipeline
that receives, processes, and exports observability data. Rather than
exporting directly from your application to a backend like Jaeger or
Datadog, you send data to the Collector.

The Collector can filter spans, scrub PII, batch data, and route it to
one or more backends. It supports two deployment patterns:

| Pattern | Description                                       |
|---------|---------------------------------------------------|
| Agent   | Runs alongside the app as a sidecar or co-process |
| Gateway | Standalone service receiving from multiple apps   |

---

Return to [OpenTelemetry](_index.md)
