# Pods

The smallest deployable unit in Kubernetes. A Pod wraps one or more containers
that share network, storage, and lifecycle.

## Notes

- [Fundamentals](fundamentals.md) - Core concepts and why Pods exist
- [Creation flow](creation-flow.md) - Control-plane path from apply to running
- [Lifecycle](lifecycle.md) - Pod phases and health checking
- [Init containers](init-containers.md) - Setup containers that run before app starts
- [Sidecar containers](sidecar-containers.md) - Native sidecar feature for helper containers
- [Scheduling](scheduling.md) - Pod placement controls
- [Resource requests and limits](resource-requests-and-limits.md) - CPU and memory allocation controls
- [QoS classes](qos-classes.md) - Resource guarantees and eviction priority
- [Hostname and DNS](hostname-dns.md) - Pod naming and DNS resolution
- [Disruptions](disruptions.md) - Pod availability guarantees
- [Graceful termination](graceful-termination.md) - Handling shutdown in practice
- [Ephemeral containers](ephemeral-containers.md) - Debugging containers for live Pods
- [Advanced configuration](advanced-configuration.md) - Runtime and resource tuning

---

Return to [Kubernetes](../_index.md)
