# Design decisions

Linkerd's architecture reflects a deliberate set of constraints. Each
decision trades flexibility for operational simplicity.

## Minimal feature surface

No built-in ingress controller, no traffic routing DSL, no Lua or
WASM plugin system. Every feature is a potential failure mode in
infrastructure software. Linkerd focuses on the core mesh
capabilities — observability, security, reliability — and stops there.

## No proxy configuration language

Proxies receive all configuration dynamically from the control plane.
There are no user-facing proxy config files. Mesh-wide policy is
expressed through a small set of Kubernetes CRDs that map directly to
proxy behaviors.

## Extensions

Capabilities outside the core mesh are packaged as extensions:

| Extension    | Purpose                                          |
|--------------|--------------------------------------------------|
| viz          | On-cluster metrics stack (Prometheus, dashboard) |
| multicluster | Cross-cluster service discovery and routing      |

Extensions are installed independently, keeping the core control
plane minimal. Telemetry export is also supported via OpenTelemetry
collectors.

## Kubernetes-native

Linkerd is built exclusively for Kubernetes. It leans on Kubernetes
primitives directly: ServiceAccounts for identity, namespaces for
policy scope, Endpoints for service discovery, admission webhooks for
proxy injection. This coupling means the mesh feels native rather
than bolted on, at the cost of not supporting other platforms.

## Intentional omissions

What the control plane does not do is as deliberate as what it does:

- No built-in metrics storage — Prometheus lives in the viz extension
- No built-in tracing collector — use an OpenTelemetry collector
- No rate limiting
- No complex traffic routing (header-based routing, fault injection,
  traffic mirroring) — traffic splits via HTTPRoute are supported,
  but Linkerd is not a full traffic management platform
- No WASM or plugin system — the proxy is a closed system
- No proxy configuration beyond annotations and CRDs

## Related

- [Architecture](architecture.md) - The structure these decisions produced
- [Proxy internals](proxy-internals.md) - Purpose-built proxy rationale
- [Automatic mTLS](mtls.md) - Zero-config security in practice

---

Return to [Linkerd](_index.md)
