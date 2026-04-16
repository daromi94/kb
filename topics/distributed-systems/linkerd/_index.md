# Linkerd

Open-source service mesh for Kubernetes. Adds observability, reliability,
and security to service-to-service traffic without any application code
changes. A transparent sidecar proxy sits next to each pod and intercepts
all traffic entering and leaving it.

## Notes

- [Architecture](architecture.md) - Control plane and data plane
- [Protocol detection](protocol-detection.md) - HTTP L7 vs opaque TCP
- [Automatic mTLS](mtls.md) - Transparent mutual TLS by default
- [Golden metrics](golden-metrics.md) - Proxy-layer traffic metrics
- [Reliability](reliability.md) - Load balancing, retries, timeouts

---

Return to [Distributed systems](../_index.md)
