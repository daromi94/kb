# Scaling mechanisms

Kubernetes has three independent autoscaling mechanisms. They solve
different problems, ship in different projects, and can be used
together or in isolation.

## The three mechanisms

| Mechanism                 | What it adjusts                        | Scope    |
|---------------------------|----------------------------------------|----------|
| Horizontal Pod Autoscaler | Number of replicas of a workload       | Workload |
| Vertical Pod Autoscaler   | CPU and memory requests/limits per Pod | Workload |
| Cluster Autoscaler        | Number of nodes in the cluster         | Cluster  |

**Horizontal Pod Autoscaler (HPA):** Built into the
kube-controller-manager. Scales the replica count up or down based on
observed metrics.

**Vertical Pod Autoscaler (VPA):** A separate project. Right-sizes
each Pod's CPU and memory requests from historical usage, leaving the
replica count alone.

**Cluster Autoscaler:** A separate project that integrates with the
cloud provider. Adds nodes when Pods cannot be scheduled and removes
nodes that are underutilized.

## Horizontal vs vertical

Horizontal scaling changes how many replicas run. Vertical scaling
changes how much each replica gets.

```text
Horizontal                 Vertical
+---+  +---+  +---+        +---------+
| P |  | P |  | P |   vs   |    P    |
+---+  +---+  +---+        |         |
                           +---------+
N small replicas           1 bigger replica
```

Horizontal is preferred for stateless request-serving workloads: it
distributes load and tolerates replica loss. Vertical fits workloads
that can't be parallelized (single-writer databases, JVMs tuned for a
fixed heap) or whose right-sized CPU and memory are hard to predict
up front.

## Combining them

HPA and Cluster Autoscaler compose naturally: HPA creates Pods, and if
the cluster runs out of capacity, Cluster Autoscaler adds nodes to
schedule them.

HPA and VPA on the same workload can conflict when both act on CPU
or memory — VPA raises the per-Pod request, which changes the
utilization ratio HPA is measuring. Run VPA in recommendation-only
mode alongside HPA, or drive HPA off a signal other than CPU/memory
(request rate, queue depth).

## Related

- [Horizontal pod autoscaler](horizontal-pod-autoscaler.md) - HPA control loop and config
- [Metrics registry](metrics-registry.md) - Where HPA reads metrics from

---

Return to [Autoscaling](_index.md)
