# Proxy injector

The proxy injector is a Kubernetes mutating admission webhook. When a
pod is created in a namespace or deployment annotated for injection,
the webhook intercepts the pod spec and adds the mesh sidecar before
the pod is scheduled.

## Injection flow

1. A namespace or deployment is annotated with
   `linkerd.io/inject: enabled`
2. A pod creation request reaches the Kubernetes API server
3. The API server calls the proxy injector webhook
4. The injector inspects the pod spec and decides whether to inject
5. If yes, it mutates the pod spec to add:
    - The `linkerd-init` init container (or CNI plugin equivalent)
    - The `linkerd2-proxy` sidecar container
    - Environment variables pointing the proxy to the control plane
    - Resource requests and limits for the proxy
    - Volume mounts for the proxy's ServiceAccount token

## Annotations

The injector's behavior is controlled through annotations on the pod
or namespace:

| Annotation                              | Effect                           |
|-----------------------------------------|----------------------------------|
| `linkerd.io/inject: enabled`            | Opt in to injection              |
| `linkerd.io/inject: disabled`           | Opt out (overrides namespace)    |
| `config.linkerd.io/skip-inbound-ports`  | Ports the proxy ignores inbound  |
| `config.linkerd.io/skip-outbound-ports` | Ports the proxy ignores outbound |
| `config.linkerd.io/proxy-cpu-request`   | Proxy CPU request                |
| `config.linkerd.io/proxy-memory-limit`  | Proxy memory limit               |
| `config.linkerd.io/opaque-ports`        | Ports treated as non-HTTP        |

Per-pod annotations override namespace-level settings. This lets
operators enable injection cluster-wide while opting out individual
workloads that are incompatible with the sidecar.

## Related

- [Traffic interception](traffic-interception.md) - What linkerd-init does after injection
- [Architecture](architecture.md) - Where the injector sits in the control plane
- [Destination service](destination-service.md) - What the proxy connects to after injection

---

Return to [Linkerd](_index.md)
