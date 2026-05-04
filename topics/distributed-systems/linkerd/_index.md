# Linkerd

Open-source service mesh for Kubernetes. Adds observability, reliability,
and security to service-to-service traffic without any application code
changes. A transparent sidecar proxy sits next to each pod and intercepts
all traffic entering and leaving it.

## Notes

- [Architecture](architecture.md) - High-level component layout
- [Destination service](destination-service.md) - Service discovery, policies, and routing
- [Proxy injector](proxy-injector.md) - Admission webhook and sidecar injection
- [Proxy internals](proxy-internals.md) - Rust runtime and dynamic config
- [Traffic interception](traffic-interception.md) - Transparent iptables redirection
- [Request lifecycle](request-lifecycle.md) - End-to-end request flow
- [Protocol detection](protocol-detection.md) - HTTP L7 vs opaque TCP
- [Automatic mTLS](mtls.md) - Transparent mutual TLS by default
- [Golden metrics](golden-metrics.md) - Proxy-layer traffic metrics
- [Reliability](reliability.md) - Failure handling in the proxy
- [Design decisions](design-decisions.md) - Architectural trade-offs
- [High availability](high-availability.md) - Production resilience and degradation

---

Return to [Distributed systems](../_index.md)
