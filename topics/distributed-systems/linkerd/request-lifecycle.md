# Request lifecycle

A request between two meshed services passes through both sidecar
proxies. The application containers on each side see a plain TCP or
HTTP connection — the mesh is invisible.

## Outbound path

1. The application sends a request to
   `service-x.namespace.svc.cluster.local`
2. iptables rules redirect the outbound connection to the local
   sidecar proxy
3. The proxy resolves the destination using endpoint data streamed
   from the destination service
4. For HTTP, the proxy selects an endpoint via EWMA load balancing
5. The proxy establishes a mutual TLS connection to the destination
   pod's proxy using its workload certificate

## Inbound path

1. The destination proxy terminates TLS and validates the caller's
   cryptographic identity
2. The proxy checks the caller against authorization policies
3. The proxy forwards the decrypted request to the application
   container on localhost

The response follows the same path in reverse. Both proxies record
metrics (latency, status codes, bytes transferred) for every request
that crosses their path.

---

Return to [Linkerd](_index.md)
