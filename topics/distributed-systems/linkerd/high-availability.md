# High availability

The control plane supports a high-availability mode that hardens it
for production use. The control plane is itself meshed — each
component pod runs its own `linkerd2-proxy` sidecar, so control
plane traffic is mTLS-encrypted like everything else in the mesh.

## HA mode

HA mode runs three replicas of each control plane component with
anti-affinity rules so replicas land on different nodes. It also
configures pod disruption budgets to prevent more than one replica
from being evicted at a time, and raises resource requests to ensure
priority scheduling.

## Graceful degradation

The destination service is the most critical component for
availability because every proxy streams from it. If the destination
service becomes unreachable, proxies do not crash or drop
connections. They continue routing traffic using their last-known
cached endpoint state.

The trade-off is that the mesh becomes stale: new deployments, scale
events, and policy changes will not reach the proxies until the
destination service recovers. Existing traffic keeps flowing, but
the mesh cannot adapt to changes.

## Related

- [Destination service](destination-service.md) - The component proxies depend on most
- [Architecture](architecture.md) - Control plane structure

---

Return to [Linkerd](_index.md)
