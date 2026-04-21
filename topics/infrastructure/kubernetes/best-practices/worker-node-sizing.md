# Worker node sizing

The same cluster capacity can be delivered by a few large nodes or
many small ones. Both cost the same in raw compute — the trade-off
is everywhere else.

## Reserved overhead

Every node reserves CPU and memory for the kubelet, the OS, and an
eviction buffer. The reservation formula is tiered, so larger nodes
pay a **smaller percentage** for the same fixed costs.

Seven 1 vCPU / 4 GB nodes lose about 7.7 GB combined to reservation.
One 4 vCPU / 32 GB node delivering the same compute loses 3.66 GB.
DaemonSets (kube-proxy, log agent, CSI driver) add another fixed
slice per node, which compounds the penalty on small clusters.

## Fragmentation

A 1 vCPU / 4 GB node hosting one 300m / 2 GB replica has almost
nothing left. A 4 vCPU / 32 GB node hosting the same replica can
fit a dozen more.

## Resiliency

Effective replication is `min(replicas, nodes)`. Five replicas
across two nodes means one node failure can take down several of
them at once. Highly-available workloads need enough nodes to
spread one replica per failure domain — via topology spread
constraints or pod anti-affinity.

## Autoscaling lead time

Cluster Autoscaler fires on **unschedulable pods**, not on
utilization. Provisioning a VM takes minutes regardless of its
size.

- Large nodes usually have headroom. Scale-ups land inside an
  existing node and the autoscaler is rarely invoked.
- Small nodes run near capacity. Every scale-up waits on a new VM
  before pods can start.

Large nodes trade occasional under-utilization for faster scaling.

## Image pull cost

Each node pulls an image once on its first pod. 13 replicas of a
1 GB image mean 1 GB downloaded on one large node, 13 GB on 13
small ones — slower startup, more bandwidth, more network-failure
surface.

A pull-through registry cache or peer-to-peer layer sharing between
nodes mitigates this when many small nodes are unavoidable.

## API server load

Kubelets poll and report to the API server continuously. Load
scales with **node count**, not cluster capacity. Many small nodes
push the control plane toward a larger instance or an HA setup that
a few large nodes would not need.

## Cluster and node limits

- 5,000 nodes per cluster (practical ceiling)
- Default 110 pods per node; cloud providers cap between 110 and 250
- Each node typically gets a /24 subnet with 254 usable IPs

Packing close to the IP limit risks **IP reuse**: a terminating
pod's address can be handed to a new pod before stale routes in
ingress, kube-proxy, or service caches have updated, briefly
sending traffic to the wrong pod. Keep max-pods well below the
subnet size.

## Storage attach slots

Cloud instances cap how many disks a VM can attach. A StatefulSet
creates one PVC per replica, so a node can host at most as many
StatefulSet replicas as it has attach slots. Larger instances
usually allow more.

## Trade-off summary

| Aspect                | Favors few large      | Favors many small     |
|-----------------------|-----------------------|-----------------------|
| Reserved overhead     | Lower percentage      | Higher percentage     |
| Fragmentation         | Less                  | More                  |
| Fault blast radius    | Larger per node loss  | Smaller per node loss |
| Replica spread        | Limited by node count | More spread available |
| Autoscaling frequency | Rarely invoked        | Often invoked         |
| Image pull cost       | Paid once per image   | Paid per node         |
| API server load       | Low                   | High                  |
| Disk slots per node   | More                  | Fewer                 |

## Mixed pools

Nothing forces every node to be the same size. A common pattern is
one general pool plus a dedicated pool for memory-heavy or GPU
workloads — letting each class of work pick its own trade-off.

## Related

- [Cluster topologies](cluster-topologies.md) - How many clusters to run
- [Node reserved resources](node-reserved-resources.md) - Overhead formulas in detail

---

Return to [Best practices](_index.md)
