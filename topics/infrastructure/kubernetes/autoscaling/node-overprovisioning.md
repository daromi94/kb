# Node overprovisioning

Overprovisioning keeps spare node capacity idle so new pods start on
existing nodes instead of waiting for the cloud provider to boot a
VM. The cost is extra always-on compute; the gain is cutting minutes
off every scale-up.

Cluster Autoscaler has no built-in proactive mode — there is no flag
for "always keep a spare node". The pattern below reproduces that
behavior using a placeholder pod and Kubernetes priority-based
preemption.

## Mechanism

A low-priority placeholder pod reserves a full node's allocatable
capacity. When a real pod would otherwise be unschedulable:

1. The scheduler finds no node with room for the real pod.
2. It preempts the lower-priority placeholder, freeing its node.
3. The real pod schedules on the freed node in seconds.
4. The evicted placeholder goes Pending.
5. Cluster Autoscaler sees the pending placeholder and adds a node.
6. The placeholder lands on the new node, restoring the spare buffer.

The real pod is unblocked by preemption, which is fast. The 3-5
minute VM boot happens in the background while the placeholder waits
for its replacement node.

## Priority setup

Preemption kicks in when a higher-priority pod can't schedule
anywhere but could fit if a lower-priority pod were evicted. To make
the placeholder the preemption victim, give it a priority below the
default of 0. Negative values are allowed:

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: overprovisioning
value: -1
globalDefault: false
description: Used by overprovisioning placeholder pods.
```

## Placeholder deployment

The placeholder uses `registry.k8s.io/pause` — a minimal Kubernetes
image that blocks forever while holding its resource requests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: overprovisioning
spec:
  replicas: 1
  selector:
    matchLabels:
      run: overprovisioning
  template:
    metadata:
      labels:
        run: overprovisioning
    spec:
      priorityClassName: overprovisioning
      containers:
        - name: reserve-resources
          image: registry.k8s.io/pause
          resources:
            requests:
              cpu: "1739m"
              memory: "5.9G"
```

The replica count sets the size of the spare buffer. Two replicas
keep two nodes' worth of headroom.

## Sizing the placeholder

Requests must match the node's **allocatable** capacity — what
remains after the OS, kubelet, eviction threshold, and DaemonSets
take their share. A 2 vCPU / 8 GB node with typical reservations
leaves roughly 1.73 vCPU and ~5.9 GB for pods, so the placeholder
requests exactly that.

- **Under-sized:** the placeholder shares a node with real pods and
  no longer reserves a whole spare node.
- **Over-sized:** the placeholder stays permanently unschedulable
  and reserves nothing.

## Trade-offs

- **Cost:** one full node per replica, always running.
- **Latency:** real pods schedule in seconds instead of 5+ minutes.

Best fit for workloads with sharp traffic spikes where scale-up
latency is user-facing. Not worth the extra compute for batch or
predictable workloads.

---

Return to [Autoscaling](_index.md)
