# Advanced configuration

Advanced Pod configurations fine-tune interaction with node hardware, signal
availability to the cluster, and account for hidden resource costs.

## Readiness gates

By default, a Pod is "Ready" based on internal probes. Readiness gates inject
external requirements into the Pod's status.

**How it works:** Define a `readinessGate` in the Pod spec. The Pod won't be
Ready (and won't receive Service traffic) until an external controller sets
that condition to `True`.

**Use case:** Ensure a cloud load balancer (AWS ALB, Google GLB) is fully
synced before the Pod receives traffic.

## Pod overhead

Container runtimes (containerd, CRI-O) and sandboxed runtimes consume resources
not accounted for in container requests.

**How it works:** Overhead is tied to the RuntimeClass. When scheduling, the
overhead is added to container requests.

**Why it matters:** Prevents node overcommitment. If a node has 100MB left and
a Pod requests 90MB with 20MB overhead, the scheduler knows it won't fit.

## RuntimeClass

Select different container runtime configurations for isolation or hardware
features.

| Runtime     | Purpose                                 |
|-------------|-----------------------------------------|
| runc        | Standard Linux containers (default)     |
| gVisor/Kata | Stronger kernel isolation for untrusted |
| Windows     | Windows Server nodes                    |

Reference in Pod spec with `runtimeClassName: my-runtime`.

## HugePages

For performance-critical applications, standard 4KiB pages cause overhead from
tracking many pages. HugePages (2MiB or 1GiB) reduce this.

**Constraint:** Pre-allocated on the node before Pods can request them.

**Usage:** Request like CPU/Memory: `hugepages-2Mi: 100Mi`. Unlike regular
memory, HugePages cannot be overcommitted.

## Extended resources

Track resources Kubernetes doesn't know natively: GPUs, FPGAs, network
bandwidth.

**Node level:** A Device Plugin advertises resources (e.g., `nvidia.com/gpu: 4`)

**Pod level:** Request like standard resources. Scheduler places Pod only on
nodes with that hardware.

## Summary

| Feature            | Purpose                   | Key benefit                                |
|--------------------|---------------------------|--------------------------------------------|
| Readiness gates    | External health signaling | Cloud LB and external network integration  |
| Pod overhead       | Resource accounting       | Prevents instability from hidden costs     |
| RuntimeClass       | Sandbox selection         | Mixed-security workloads (e.g., gVisor)    |
| HugePages          | Memory optimization       | Lower TLB misses for high-performance apps |
| Extended resources | Hardware awareness        | Schedule onto GPUs or specialized hardware |
