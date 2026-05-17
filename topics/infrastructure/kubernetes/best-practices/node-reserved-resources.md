# Node reserved resources

A Kubernetes node does not offer all its CPU and memory to pods.
The kubelet, the OS, and an eviction buffer are carved out first,
and the scheduler only sees what's left:

```text
Allocatable = Capacity − Kube reserved − System reserved − Eviction
```

## The three slices

- **Kube reserved** — the kubelet and container runtime
- **System reserved** — OS daemons, SystemD, sshd
- **Eviction threshold** — a memory safety margin. When free memory
  drops below it the kubelet evicts pods to save the node from an
  OOM. Typically, 100 MB.

The two "reserved" slices are configurable. Cloud providers ship
tiered defaults that reserve a **smaller fraction** of larger
instances.

## CPU tiers

| Core position | Reservation     |
|---------------|-----------------|
| 1st core      | 6% of that core |
| 2nd core      | 1% of that core |
| 3rd-4th core  | 0.5% of each    |
| 5th core on   | 0.25% of each   |

A 4-core node reserves roughly `60m + 10m + 10m = 80m` — under 2%
of total CPU, even on a small instance.

## Memory tiers

| Memory band      | Reservation |
|------------------|-------------|
| Under 1 GB total | 255 MiB     |
| First 4 GB       | 25%         |
| 4 GB to 8 GB     | 20%         |
| 8 GB to 16 GB    | 10%         |
| 16 GB to 128 GB  | 6%          |
| Above 128 GB     | 2%          |

An 8 GB node reserves $(25\% \times 4) + (20\% \times 4) = 1 + 0.8 = 1.8$ GB
for the kubelet, plus 100 MB for eviction. About **24% of the node
is gone** before any pod runs.

## Overhead drops with size

| Node size      | Reserved (approx) | Memory usable |
|----------------|-------------------|---------------|
| 1 vCPU / 4 GB  | 60m / 1.1 GB      | ~73%          |
| 2 vCPU / 8 GB  | 70m / 1.9 GB      | ~76%          |
| 4 vCPU / 16 GB | 80m / 2.7 GB      | ~83%          |
| 4 vCPU / 32 GB | 80m / 3.66 GB     | ~89%          |

Small nodes pay the reservation tax on every node. Seven 1 vCPU /
4 GB nodes lose ~7.7 GB combined. One 4 vCPU / 32 GB node with the
same compute loses 3.66 GB.

DaemonSets (kube-proxy, log agent, DNS cache, CSI driver) add
another **fixed** per-node cost on top, which compounds the penalty
on small clusters.

---

Return to [Best practices](_index.md)
