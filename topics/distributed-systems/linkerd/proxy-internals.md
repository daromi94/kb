# Proxy internals

`linkerd2-proxy` is a purpose-built sidecar proxy written in Rust. It
runs on the Tokio async runtime and uses the Tower middleware ecosystem
for composable request processing. Unlike general-purpose proxies, it
serves a single role: Kubernetes service mesh sidecar.

## Why Rust

A per-pod sidecar multiplies its resource cost across every pod in
the cluster. Rust provides memory safety through compile-time
guarantees rather than garbage collection. No GC pauses means
predictable tail latencies — important for a component sitting in the
hot path of every request.

The narrow scope also matters. A purpose-built proxy carries less
code, a smaller configuration surface, and a smaller attack surface.

## Dynamic configuration

The proxy has no user-facing configuration files. All routing, policy,
and endpoint data arrives from the control plane over gRPC
server-streaming RPCs. When the destination service detects a change
(new endpoints, updated policy), it pushes the update to every
connected proxy immediately. This push-based model means fast
convergence after changes and lower load on the Kubernetes API server
compared to polling.

No proxy config files means no proxy-config misconfiguration.

## Related

- [Architecture](architecture.md) - Where the proxy fits
- [Traffic interception](traffic-interception.md) - How traffic reaches the proxy
- [Protocol detection](protocol-detection.md) - What happens after traffic arrives

---

Return to [Linkerd](_index.md)
