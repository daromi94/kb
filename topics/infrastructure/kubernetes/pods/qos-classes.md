# QoS classes

Quality of Service (QoS) determines which Pods are evicted first when a node
runs out of resources. Kubernetes infers the class from how you define
container `requests` and `limits`.

## Class assignment

### Guaranteed (highest priority)

Last to be killed. Resources are reserved exclusively.

**Requirement:** Every container has CPU and memory limits **and** requests
defined, and they are **exactly equal**.

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

### Burstable (standard)

Most common class. Guaranteed the request amount but can burst higher.

**Requirement:** At least one container has a request or limit, but they are
not equal, or some containers lack limits.

```yaml
resources:
  requests:
    memory: "128Mi"
  limits:
    memory: "256Mi"
```

### BestEffort (lowest priority)

First to be evicted. Runs on leftover resources with no guarantees.

**Requirement:** No containers have any CPU or memory requests or limits.

## Eviction hierarchy

When a node is under memory pressure, the kubelet evicts in order:

1. **BestEffort** Pods
2. **Burstable** Pods using more memory than requested
3. **Guaranteed** Pods (and Burstable using less than request)

## Summary

| QoS class  | Resource config                  | Eviction priority | Use case                     |
|------------|----------------------------------|-------------------|------------------------------|
| Guaranteed | Requests == Limits (all)         | Lowest (last)     | Critical DBs, production API |
| Burstable  | Requests < Limits (at least one) | Medium            | General microservices        |
| BestEffort | No requests or limits            | Highest (first)   | Batch processing, scripts    |

## Troubleshooting

If Pods randomly restart with `OOMKilled` status, they likely have BestEffort
or Burstable class and the node ran out of memory. Set appropriate requests and
limits based on actual usage to improve stability.
