# Horizontal Pod Autoscaler

The Horizontal Pod Autoscaler (HPA) scales a workload by adjusting its
replica count in response to observed metrics. It is a controller in
the kube-controller-manager, configured declaratively by creating a
HorizontalPodAutoscaler resource.

HPA can target any workload that exposes the `/scale` subresource,
including Deployment, StatefulSet, ReplicaSet, and ReplicationController.
DaemonSets cannot be horizontally scaled.

## Control loop

Every sync period, the controller runs three steps for each HPA:

```text
+---------------------------+
|  1. Query scaling metric  |
|        from metrics API   |
+-------------+-------------+
              |
              v
+---------------------------+
|  2. Calculate desired     |
|        replica count      |
+-------------+-------------+
              |
              v
+---------------------------+
|  3. Scale workload to     |
|        desired count      |
+---------------------------+
```

The sync period defaults to 15 seconds and is set with the
`--horizontal-pod-autoscaler-sync-period` flag on the controller
manager.

## Scaling formula

```text
desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))
```

Concretely, with a per-Pod target of 10 req/sec:

| Current metric | Current replicas | Desired replicas     |
|----------------|------------------|----------------------|
| 20 req/sec     | 3                | 6                    |
| 2 req/sec      | 3                | 1                    |
| 11 req/sec     | 3                | 3 (within tolerance) |

**Tolerance:** If the ratio `currentMetric / targetMetric` is within a
small band of 1.0 (default 0.1), the HPA skips scaling. This prevents
thrashing on noisy metrics.

## HorizontalPodAutoscaler resource

The manifest specifies the target workload, a replica range, and one
or more metrics with per-metric target values.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Pods
      pods:
        metric:
          name: myapp_requests_per_second
        target:
          type: AverageValue
          averageValue: 2
```

This scales the `myapp` Deployment between 1 and 10 replicas to keep
the per-Pod request rate near 2 req/sec.

**Metric types** in the `metrics` array:

| Type     | Source                               | Typical use                        |
|----------|--------------------------------------|------------------------------------|
| Resource | Resource Metrics API (CPU/memory)    | Classic CPU-based scaling          |
| Pods     | Custom Metrics API, averaged per Pod | Per-replica rates (req/sec, depth) |
| Object   | Custom Metrics API, one K8s object   | Ingress QPS, queue length on a CR  |
| External | External Metrics API                 | Cloud queue length, SaaS metric    |

When multiple metrics are configured, HPA computes a desired replica
count for each and picks the maximum.

## Related

- [Autoscaling types](autoscaling-types.md) - HPA vs VPA vs Cluster Autoscaler
- [Metrics registry](metrics-registry.md) - How metrics reach the HPA

---

Return to [Autoscaling](_index.md)
