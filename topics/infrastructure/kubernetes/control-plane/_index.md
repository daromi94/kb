# Control plane

The components that accept declarative intent, decide cluster state,
and push changes out to every node.

## Notes

- [API server](api-server.md) - HTTP front door to the cluster
- [Admission controllers](admission-controllers.md) - Policy gates for writes
- [Server-Side Apply](server-side-apply.md) - Multi-manager declarative updates
- [Watch API](watch-api.md) - Change notification streams
- [API extension](api-extension.md) - Adding new resource types

---

Return to [Kubernetes](../_index.md)
