# Pods

The smallest deployable unit in Kubernetes. A Pod wraps one or more containers
that share network, storage, and lifecycle.

## Notes

- [Fundamentals](fundamentals.md) - Core concepts and why Pods exist
- [Lifecycle](lifecycle.md) - Phases, container states, probes, and termination
- [Init containers](init-containers.md) - Setup containers that run before app starts
- [Sidecar containers](sidecar-containers.md) - Native sidecar feature for helper containers
- [Ephemeral containers](ephemeral-containers.md) - Debugging containers for live Pods
- [Disruptions](disruptions.md) - Voluntary and involuntary disruptions with PDBs
- [Hostname and DNS](hostname-dns.md) - Pod naming and DNS resolution
- [QoS classes](qos-classes.md) - Resource guarantees and eviction priority
- [Advanced configuration](advanced-configuration.md) - Overhead, RuntimeClass, HugePages
- [Scheduling](scheduling.md) - Affinity, taints, and topology spread
