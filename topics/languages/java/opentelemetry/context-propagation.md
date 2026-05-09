# Context and propagation

Context and propagation are how OpenTelemetry maintains trace continuity
across threads, services, and transport boundaries.

## Context

Context is an immutable bag of key-value pairs that travels with a
request's execution. It carries the current Trace ID and Span ID.

In Java, the default ContextStorage uses a ThreadLocal to hold the
active Context. This storage is pluggable — alternative implementations
exist for reactive frameworks and virtual threads. Context can also be
passed explicitly without relying on implicit thread-local storage.

## Propagation

When a request crosses a process boundary — an HTTP call to another
service, a message to a Kafka topic — the Context must go with it.
Propagation serializes the Context into carrier headers and
deserializes it on the receiving side.

The default propagator uses the W3C TraceContext specification, which
defines the `traceparent` and `tracestate` HTTP headers. The
`traceparent` header encodes the Trace ID, parent Span ID, and trace
flags in a single string.

The receiving service extracts these headers, reconstructs the Context,
and continues the trace as a child of the propagated Span.

---

Return to [OpenTelemetry](_index.md)
