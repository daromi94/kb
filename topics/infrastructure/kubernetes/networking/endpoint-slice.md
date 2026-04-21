# EndpointSlice

A Service routes traffic to a changing set of Pods. An EndpointSlice
stores the actual IP:port pairs behind a Service — the addresses
that kube-proxy rewrites packets to when they hit the Service's
ClusterIP. Each Service gets one or more slices, maintained by the
EndpointSlice controller.

Splitting endpoints across multiple small slices is a scale choice:
a Service with thousands of backends would otherwise produce one
giant object that every watcher has to re-read on every update.
With slices, updates only touch the slice that changed.

## How endpoints are populated

The controller watches Pods whose labels match the Service selector.
For every matching Pod it records the Pod's IP, the Service's
`targetPort` resolved against that Pod, and the Pod's readiness
state.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 3000
```

Every Pod labeled `app: nginx` contributes one entry. kube-proxy
reads the slices and programs the dataplane to DNAT Service IP:80
to Pod IP:3000.

## Endpoint conditions

Each entry carries three condition flags:

| Condition   | Meaning                                     |
|-------------|---------------------------------------------|
| ready       | Pod passed readiness and is not terminating |
| serving     | Pod is serving traffic regardless of state  |
| terminating | Pod has been marked for deletion            |

A Pod that fails readiness is **not removed** from the slice — its
`ready` flag flips to `false`. kube-proxy skips `ready: false`
entries for normal traffic, but may still route to entries where
`serving: true` and `terminating: true` during graceful shutdown.

## Update triggers

The controller rewrites a slice when:

- A Pod matching the selector is created or deleted
- A Pod's labels change, adding or removing it from the match
- A Pod's readiness, serving, or terminating condition changes

Each update fans out as a watch event to every client of that slice
— primarily kube-proxy on each node, plus in-cluster load balancers
and Gateway API controllers.

## Related

- [kube-proxy](kube-proxy.md) - Consumes EndpointSlices to program DNAT

---

Return to [Networking](_index.md)
