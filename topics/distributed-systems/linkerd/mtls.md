# Automatic mTLS

Every connection between two meshed pods is encrypted and authenticated
with mutual TLS by default. Application code and its configuration are
not involved — mTLS is negotiated and terminated entirely inside the
sidecar proxies on each end of the connection.

## Workload identity

The control plane's identity service is a certificate authority for
the cluster. When a proxy starts, it submits a certificate signing
request using its pod's Kubernetes ServiceAccount token as proof of
identity. The identity service verifies that token against the
Kubernetes API and issues a short-lived leaf certificate (roughly a
day) bound to the ServiceAccount.

Workload identity in Linkerd is therefore the Kubernetes
ServiceAccount, not the pod name, IP, or DNS hostname. These change
constantly as pods churn; the ServiceAccount is stable.

## Authorization policy

Because every mTLS connection carries a verified workload identity,
authorization policies can be written in terms of "ServiceAccount A
may talk to ServiceAccount B on port X." The policy controller
evaluates those rules and pushes the resulting allow/deny decisions
to the proxies, which enforce them at connection time.

## Trust anchor

The leaf certificates the identity service hands out chain up to a
**trust anchor** — a long-lived root certificate that every proxy is
configured with. Rotating the trust anchor requires coordinating
across every proxy in the cluster, so it is kept distinct from the
short-lived leaf certs that rotate automatically.

---

Return to [Linkerd](_index.md)
