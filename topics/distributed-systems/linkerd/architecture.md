# Architecture

Linkerd splits into two planes. A **control plane** runs centrally in
the cluster and configures the mesh. A **data plane** of lightweight
sidecar proxies attaches to every meshed pod and carries the actual
traffic.

## Data plane

The data plane is a collection of `linkerd2-proxy` sidecars — one per
application pod. The proxy is written in Rust and intercepts every TCP
connection entering or leaving the pod. It handles mTLS, routing,
retries, load balancing, and metric collection on behalf of the
application.

Because the proxy is purpose-built for the mesh use case rather than a
general-purpose reverse proxy, it has a small resource footprint and
low per-hop latency.

## Control plane

The control plane runs as a set of Kubernetes Deployments in a dedicated
namespace (`linkerd` by default). It is written primarily in Go.

| Component      | Role                                                 |
|----------------|------------------------------------------------------|
| destination    | Service discovery and routing policy for proxies     |
| identity       | Certificate authority; issues per-workload TLS certs |
| proxy-injector | Mutating webhook that adds sidecars to new pods      |
| policy         | Evaluates authorization policies for proxies         |

The policy controller is not a separate deployment. It runs as a
container inside the destination pod and shares its lifecycle.

## Data flow

```
+---------------------------+
|  Application pod          |
|                           |
|  +---------------------+  |
|  |  app container      |  |
|  +---------------------+  |
|            |              |
|            v              |        +------------------+
|  +---------------------+  | config |  control plane   |
|  |  linkerd2-proxy     |<--------- |  destination     |
|  |  (sidecar)          |     certs |  identity        |
|  +---------------------+<----------|  proxy-injector  |
|            |              |        +------------------+
+------------|--------------+
             v
          network
```

## Related

- [Automatic mTLS](mtls.md) - How identity issues proxy certs
- [Protocol detection](protocol-detection.md) - How proxies classify traffic
- [Golden metrics](golden-metrics.md) - What the proxy measures

---

Return to [Linkerd](_index.md)
