# CoreDNS

CoreDNS is the default cluster DNS server. Pods use it to reach Services and
each other by stable names rather than ephemeral IPs, and it forwards
anything outside the cluster domain to upstream resolvers.

## Where it lives

CoreDNS runs as a Deployment named `coredns` in `kube-system`, fronted by a
ClusterIP Service. The Service is still called `kube-dns` so that clients
configured against the old server keep working.

## How pods reach it

With the default `ClusterFirst` DNS policy, kubelet writes `/etc/resolv.conf`
inside each pod using its own `clusterDNS` and `clusterDomain` settings:
`nameserver` points at the CoreDNS Service IP and `search` is built from the
cluster domain. Pods with `dnsPolicy: Default` inherit the node's resolver
instead and never see CoreDNS.

## Resolving Kubernetes names

The `kubernetes` plugin watches the API server for Services, EndpointSlices,
Pods, and Namespaces, and generates records as those resources change. A
Service like `payments` in namespace `app` becomes
`payments.app.svc.cluster.local`, resolving to its ClusterIP (A, AAAA, or
both, depending on the Service's IP families). Pods get records of the form
`<pod-ip-dashed>.<namespace>.pod.cluster.local`, and headless Services also
get SRV records plus one A record per backing pod. Once CoreDNS returns a
ClusterIP, `kube-proxy` (or an equivalent CNI data plane) takes over and
routes packets to a real pod.

## Plugin chain

A query traverses a chain of plugins in declaration order. Each plugin
either answers it or falls through to the next.

| Plugin      | Role                                             |
|-------------|--------------------------------------------------|
| kubernetes  | Resolves names inside the cluster domain         |
| forward     | Sends non-cluster queries to upstream resolvers  |
| cache       | Caches positive and negative answers in memory   |
| prometheus  | Exposes query metrics for scraping               |
| errors      | Logs errors from other plugins                   |
| health      | HTTP liveness endpoint                           |
| ready       | HTTP endpoint signalling plugins are initialised |
| loop        | Detects forwarding loops at startup              |
| reload      | Picks up Corefile changes without restart        |
| loadbalance | Randomises record order in responses             |

## The Corefile

CoreDNS is driven by a single config file, the Corefile, shipped as the
`coredns` ConfigMap in `kube-system`. A stock one looks like:

```text
.:53 {
    errors
    health {
        lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
        ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
}
```

---

Return to [Networking](_index.md)
