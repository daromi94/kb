# Disruptions

A disruption is any event that causes a Pod to go down. Kubernetes classifies
these as voluntary (intentional) or involuntary (unavoidable).

## Disruption types

| Type        | Examples                                    | Mitigation                   |
|-------------|---------------------------------------------|------------------------------|
| Involuntary | Hardware failure, kernel panic, OOM kill    | Replication, resource limits |
| Voluntary   | Node drain, Deployment update, scaling down | PodDisruptionBudget          |

### Involuntary disruptions

Events Kubernetes cannot predict:

- Hardware failure (power loss, disk failure)
- Kernel panic
- Network partition (node disappears from control plane)
- Eviction due to resource pressure (node runs out of RAM/CPU)

### Voluntary disruptions

Caused by human actions or automated administrative tasks:

- Running `kubectl drain` for maintenance
- Updating a Deployment (replacing old Pods)
- Scaling down replicas
- Accidentally deleting a Pod

## PodDisruptionBudget

A PDB limits how many Pods can be down simultaneously during voluntary
disruptions. It ensures Kubernetes blocks operations that would take your
application below a safety threshold.

### Configuration options

Use one of these mutually exclusive fields:

| Field            | Description                                 | Example      |
|------------------|---------------------------------------------|--------------|
| `minAvailable`   | Minimum Pods that must always be running    | `2` or `50%` |
| `maxUnavailable` | Maximum Pods that can be taken down at once | `1` or `10%` |

### Example manifest

Ensure at least two Zookeeper replicas are always available:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: zk-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: zookeeper
```

### PDB enforcement

If `kubectl drain node-1` would bring Pods below `minAvailable`, the eviction
fails. The drain command waits and retries until either:

- The PDB is satisfied (another Pod starts on a different node)
- The admin manually intervenes

## Best practices

**Don't use PDBs for single-replica apps:** If `minAvailable: 1` with only one
Pod, Kubernetes can never voluntarily move that Pod, blocking node maintenance.

**Set reasonable limits:** With 3 replicas, `maxUnavailable: 1` is safer than
`minAvailable: 3` (which would allow zero disruptions).

**Combine with Topology Spread Constraints:** Ensure disruptions don't take
down all Pods in a single availability zone.
