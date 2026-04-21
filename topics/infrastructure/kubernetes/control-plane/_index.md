# Control plane

Clients declare desired state; the control plane — API server,
etcd, scheduler, controller managers — continuously reconciles the
cluster toward it.

## Notes

- [API server](api-server.md) - HTTP front door to the cluster
- [Admission controllers](admission-controllers.md) - Policy gates for writes
- [Server-Side Apply](server-side-apply.md) - Multi-manager declarative updates
- [Watch API](watch-api.md) - Change notification streams
- [API extension](api-extension.md) - Adding new resource types

---

Return to [Kubernetes](../_index.md)
