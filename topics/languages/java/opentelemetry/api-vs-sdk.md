# API vs SDK

OpenTelemetry separates its interface from its implementation. This
split determines how you manage dependencies and where you configure
telemetry.

## The API

The API (`opentelemetry-api`) is a set of interfaces for creating
telemetry data. Instrumentation code calls the API to create spans,
record metrics, and emit logs:

```java
Span span = tracer.spanBuilder("my-operation").startSpan();
```

The API is a no-op by default — it does nothing and consumes near-zero
resources unless an SDK is registered. This makes it safe to depend on
unconditionally. Library authors code against the API so their
libraries emit telemetry without forcing a specific backend or
configuration on consumers.

## The SDK

The SDK (`opentelemetry-sdk`) is the concrete implementation. It
collects the data generated through the API, applies sampling rules,
batches spans, and exports them.

Configure the SDK only in your final runnable application, never in a
shared library. This keeps the decision of *where telemetry goes* and
*how much to sample* in the hands of the application operator.

## Related

- [Data pipeline](data-pipeline.md) - Exporters and the Collector
- [Signals](signals.md) - The three types of telemetry data

---

Return to [OpenTelemetry](_index.md)
