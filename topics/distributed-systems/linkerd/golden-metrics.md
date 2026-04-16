# Golden metrics

The moment a workload is meshed, Linkerd begins recording three core
traffic metrics for every service-to-service call. No application
instrumentation is required — the proxy already sees the traffic, so
it measures it.

## The three metrics

| Metric       | Meaning                                             |
|--------------|-----------------------------------------------------|
| Success rate | Share of responses that are not errors              |
| Request rate | Requests per second flowing through the service     |
| Latency      | Response time distribution, typically p50, p95, p99 |

Linkerd's term is *golden metrics*, and it stops at three. Saturation
is not included, which differentiates the vocabulary from Google SRE's
"four golden signals."

## HTTP vs TCP coverage

The three metrics apply to traffic the proxy can parse at L7 — HTTP,
HTTP/2, and gRPC — where request and response boundaries exist. For
opaque TCP connections the proxy still reports bytes in and out plus
connection counts, but it cannot compute per-request success rate or
latency. A byte stream has no notion of a request.

## Why this matters

Observability requires no setup beyond meshing the service — no client
library, no span instrumentation, no tracing backend.

## Related

- [Protocol detection](protocol-detection.md) - Why TCP gets fewer metrics
- [Architecture](architecture.md) - Where measurement happens
- [Reliability](reliability.md) - How the proxy reacts to slow endpoints

---

Return to [Linkerd](_index.md)
