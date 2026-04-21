# Cluster Autoscaler

The Cluster Autoscaler (CA) adjusts the number of nodes in a cluster.
It adds nodes when pods cannot be scheduled and removes nodes that
sit underutilized.

CA ships from the kubernetes/autoscaler project and runs as its own
Deployment, not inside the kube-controller-manager. It drives the
cloud provider's node groups — AWS Auto Scaling Groups, GCP Managed
Instance Groups, Azure Scale Sets — to provision and decommission
VMs.

## Scale-up trigger

CA scales up on **unschedulable pods**, not on utilization or memory
pressure. When the scheduler cannot place a pod, it writes a
PodCondition with `status: False` and `reason: Unschedulable`. CA
watches the API server for pods carrying that condition.

```
+-------------------+     +--------------------+
| Scheduler cannot  |     | Cluster Autoscaler |
| place Pod -> sets |---->| sees condition,    |
| Unschedulable     |     | runs scale-up      |
+-------------------+     +--------------------+
```

The scheduler already knows how to bin-pack, weighing requests,
taints, affinity, topology spread, and DaemonSet overhead. CA does
not duplicate that logic. It waits for the scheduler to fail and
treats that failure as its signal.

Latency is the trade-off. A full scale-up walks through six steps:

1. Scheduler rejects the pod.
2. CA observes the Unschedulable condition.
3. CA selects a node group and issues a provision call.
4. The cloud provider boots a VM.
5. The kubelet registers the new node.
6. The scheduler places the pending pod.

End-to-end this takes minutes, dominated by VM boot time.

## Node group templates

CA never compares pod requests directly against existing node
capacity. For each node group it builds a **template node** —
what a fresh node from that group would look like — and simulates
scheduling the pending pod against each template. The first group
whose template fits wins.

Two node groups with identical instance types can behave differently
if their taints, labels, or DaemonSets differ. The pod must match
the template, not just the machine.

## Scale-down

A node becomes a scale-down candidate when its aggregate utilization
stays below a threshold for a minimum duration:

| Setting                            | Default |
|------------------------------------|---------|
| `scale-down-utilization-threshold` | 0.5     |
| `scale-down-unneeded-time`         | 10m     |

If both conditions hold and the node's pods can be rescheduled
elsewhere, CA drains and removes it. PodDisruptionBudgets are
respected: if evicting a replica would violate a PDB, CA leaves the
node alone.

Some pods block scale-down entirely — kube-system pods, pods with
local storage, and pods referencing node-specific volumes. Annotate
them `cluster-autoscaler.kubernetes.io/safe-to-evict: "true"` to
allow removal.

## Why HPA outpaces CA

HPA reacts in seconds. Its sync period is 15s, and it only edits a
replica count. CA reacts in minutes because it waits on a cloud
provider to boot a VM. A traffic spike creates pods faster than CA
can add nodes, leaving replicas Pending until capacity arrives.

Over-provisioning absorbs the gap. Keep a buffer of idle capacity
using low-priority placeholder pods that get evicted when real
pods need the space, or run a small pool of oversized nodes so HPA
has room to grow into while CA catches up.

## Related

- [Autoscaling types](autoscaling-types.md) - HPA vs VPA vs Cluster Autoscaler
- [Horizontal Pod Autoscaler](horizontal-pod-autoscaler.md) - Replica-count control loop
- [Node reserved resources](../best-practices/node-reserved-resources.md) - What reduces schedulable capacity

---

Return to [Autoscaling](_index.md)
