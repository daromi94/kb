# Protocol detection

The Linkerd proxy intercepts every TCP connection for its pod, but not
all connections get the same treatment. When a new connection opens,
the proxy peeks at the first bytes of the stream, classifies the
protocol, and routes the connection into one of two pipelines.

## HTTP pipeline

HTTP/1.1, HTTP/2, and gRPC flow through a full L7 pipeline. The proxy
parses individual requests, applies per-route configuration, records
per-request metrics, and can retry idempotent calls. Nearly all of
Linkerd's observability and traffic-management features depend on
this path.

## Opaque TCP pipeline

Non-HTTP connections are proxied as opaque byte streams. The proxy
still terminates mTLS and reports byte-level metrics and connection
counts, but it cannot see request boundaries inside the stream, so it
cannot route, retry, or compute per-request latency.

## Related

- [Architecture](architecture.md) - Where the proxy sits
- [Golden metrics](golden-metrics.md) - Why TCP has fewer metrics
- [Reliability](reliability.md) - Retries require the HTTP pipeline

---

Return to [Linkerd](_index.md)
