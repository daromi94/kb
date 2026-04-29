# CoreDNS

CoreDNS is the cluster DNS server. It turns Service names into ClusterIPs
and forwards anything outside the cluster domain to upstream resolvers.

It runs as a Deployment in `kube-system` behind a ClusterIP Service. Each
pod's `/etc/resolv.conf` is written by the kubelet at start-up, with
`nameserver` pointing at that Service IP and `search` built from the
cluster domain — so lookups reach CoreDNS without the pod knowing it.

## Resolving names

The `kubernetes` plugin watches the API server and generates A/AAAA
records as Services change. A Service `payments` in namespace `app`
becomes `payments.app.svc.cluster.local`, resolving to its ClusterIP.
Anything outside the cluster domain falls through to the `forward` plugin,
which sends it to the node's upstream resolvers.

## Plugin chain

A query traverses a chain of plugins in declaration order. Each plugin
either answers it or falls through to the next.

| Plugin       | Role                                            |
|--------------|-------------------------------------------------|
| `kubernetes` | Resolves names inside the cluster domain        |
| `forward`    | Sends non-cluster queries to upstream resolvers |
| `cache`      | Caches positive and negative answers in memory  |
| `prometheus` | Exposes query metrics for scraping              |

Other directives in the default Corefile (`errors`, `health`, `ready`,
`loop`, `reload`, `loadbalance`) cover lifecycle, health-check endpoints,
and response shuffling.

## The corefile

CoreDNS is driven by a single config file, the Corefile, shipped as the
`coredns` ConfigMap in `kube-system`. The default looks like this:

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

## Related

- [kube-proxy](kube-proxy.md) - Routes the ClusterIP that CoreDNS returns

---

Return to [Networking](_index.md)
