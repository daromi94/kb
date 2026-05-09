# Lead time

The time from a traffic spike to a new pod serving requests is the
sum of four sequential delays: HPA reaction, CA reaction, VM
provisioning, and pod startup. On a fresh node, a worst-case cold
scale-up takes around **6-7 minutes**.

## The four contributors

| Stage           | What happens                                      | Typical worst case |
|-----------------|---------------------------------------------------|--------------------|
| HPA reaction    | Metric reaches HPA; replica count increases       | ~1m25s             |
| CA reaction     | Unschedulable pod seen; node group picked         | 30s to 60s         |
| VM provisioning | Cloud provider boots the VM and kubelet registers | 3 to 5 minutes     |
| Pod startup     | Image pulled, container started                   | Seconds to ~1m     |

Each stage gates the next. HPA must scale before CA sees a pending
pod, CA must fire before the cloud provider boots, and the node must
register before the pod can start. The total is additive.

## HPA reaction breakdown

Three pipelined loops move a metric into an HPA decision:

| Interval                      | Default |
|-------------------------------|---------|
| kubelet pod-usage scrape      | 10s     |
| Metrics Server scrape kubelet | 60s     |
| HPA controller sync period    | 15s     |

Worst case these align adversely and the metric waits the full
interval at each hop, around 85s end to end.

## CA reaction

CA scans for unschedulable pods every 10s (`--scan-interval`). Once
one is detected, decision time depends on cluster size:

| Cluster size   | Worst case | Average |
|----------------|------------|---------|
| <100 nodes     | 30s        | 5s      |
| 100-1000 nodes | 60s        | 15s     |

Counting scan interval plus decision, total CA delay is roughly 40s
on small clusters and 70s on larger ones.

## VM provisioning

This stage dominates the total and sits outside cluster control.
Booting a cloud VM and having its kubelet register with the API
server typically takes 3 to 5 minutes. AWS, Azure, and GCP are all
in the same range; spot and preemptible pools are not materially
faster.

## Pod startup

Once the node exists, container runtime startup is milliseconds. The
variable cost is **image pull time**. A cold node fetching a
multi-GB image from a remote registry can take a minute or more; a
node that already has the image cached starts in seconds.

## Worst-case total

```text
HPA delay:         1m25s
CA delay:          0m30s  (small cluster)
VM provisioning:   4m
Image pull:        0m30s
===================
Total:             6m25s
```

On clusters above 100 nodes, the extra CA latency lifts the total
toward ~7 minutes.

## Reducing lead time

Tuning the cluster-side loops only buys back tens of seconds — the
VM boot dominates everything else combined. The usual approaches:

- **Tighten control-plane intervals.** Lower the HPA sync period,
  Metrics Server resolution, and CA scan interval. Trades
  control-plane CPU for faster signal propagation.
- **Pre-pull images onto nodes.** Pre-baked AMIs, DaemonSet pullers,
  or peer-to-peer image distribution populate the local cache so
  pod startup drops to near zero.
- **Over-provision nodes.** Keep idle capacity running so new pods
  land on existing nodes and skip the CA and VM stages entirely.
  The common implementation uses low-priority placeholder pods that
  get evicted when real pods need the space.
- **Scale up proactively.** Trigger extra nodes on a schedule or on
  leading indicators (queue depth, upstream request rate) so VMs are
  already booted by the time traffic arrives.

Only the last two eliminate VM provisioning from the critical path.
The first two shrink the non-VM portion, which is already the
smaller share.

---

Return to [Autoscaling](_index.md)
