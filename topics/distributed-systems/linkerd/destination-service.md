# Destination service

The destination deployment is the most complex component in the
control plane. It bundles three logical services in a single pod:
the destination server (service discovery and routing), the SP
validator (ServiceProfile admission checks), and the policy
controller (authorization). Every proxy in the mesh depends on it.

## Subscription model

Each proxy maintains a long-lived gRPC stream to the destination
server. When a proxy needs endpoints for a service, it opens a `Get`
stream and holds it open. The destination server watches the
Kubernetes API for EndpointSlices, then fans out updates only to
proxies that have subscribed to that particular service.

This fan-out design has three consequences:

- The Kubernetes API is watched once per service by the destination
  server, not once per proxy. Five hundred proxies calling the same
  service produce one API watch, not five hundred.
- Endpoint changes propagate in milliseconds. A pod going away
  triggers an immediate push to every subscribed proxy.
- Each endpoint update carries the pod IP, port, weight, TLS
  identity, and protocol hints.

## ServiceProfile lookups

When a proxy subscribes to a destination, the destination server
also checks whether a ServiceProfile exists for that service. If one
does, the server streams down per-route definitions, retry policies,
and timeout configuration. The proxy matches incoming requests
against route patterns from the profile and applies route-specific
behavior.

## Opaque port handling

The destination server tells proxies which ports should be treated
as opaque (non-HTTP). When a port is marked opaque, the proxy skips
protocol detection and forwards the stream as raw TCP with mTLS.
This is necessary for protocols like MySQL, Redis, and SMTP that
break if the proxy tries to parse them as HTTP.

## SP validator

A Kubernetes validating admission webhook running in the same pod.
It intercepts ServiceProfile creation and update requests and rejects
invalid resources — malformed regular expressions in route specs,
nonsensical retry budgets, structural violations. Catching these at
apply-time prevents silent misconfigurations from reaching the
proxies.

## Policy controller

The policy controller watches authorization-related CRDs and
translates them into rules that proxies enforce on inbound traffic.

| CRD                   | Purpose                                   |
|-----------------------|-------------------------------------------|
| Server                | Declares a port and its protocol          |
| AuthorizationPolicy   | Defines access control for a Server       |
| MeshTLSAuthentication | Authenticates peers by mesh identity      |
| NetworkAuthentication | Authenticates peers by IP CIDR range      |
| HTTPRoute             | Route-level matching for per-route policy |

## Policy flow

1. An operator creates an AuthorizationPolicy granting a specific
   ServiceAccount access to a port
2. The policy controller watches the resource and computes the
   effective policy for each Server
3. When a proxy streams its inbound policy from the destination
   service, it receives these authorization rules
4. On every inbound request, the proxy checks the peer's mTLS
   identity against the policy and allows or rejects the call

## Related

- [Architecture](architecture.md) - Where the destination deployment sits
- [Proxy internals](proxy-internals.md) - How proxies consume the gRPC streams
- [Automatic mTLS](mtls.md) - Identities the policy controller authorizes
- [Protocol detection](protocol-detection.md) - What opaque ports bypass

---

Return to [Linkerd](_index.md)
