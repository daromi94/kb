# DaemonSets

A DaemonSet ensures a specific Pod runs on every node (or a subset of nodes) in
the cluster. Unlike Deployments with explicit replica counts, DaemonSets scale
automatically with cluster size—adding Pods when nodes join and garbage
collecting them when nodes leave.

## Use Cases

DaemonSets are typically used for infrastructure-level services that must exist
on every machine:

- **Log collection:** Aggregators like Fluentd or Logstash collecting logs from
  each node
- **Monitoring:** Agents like Prometheus Node Exporter, Datadog, or New Relic
  gathering host metrics
- **Storage daemons:** Distributed storage systems like GlusterFS or Ceph where
  each node contributes storage
- **Networking:** The kube-proxy or CNI plugins (Calico, Flannel)

## Scheduling Control

By default, a DaemonSet places a Pod on every node. Control placement with:

- **Node selectors and affinity:** Target nodes with specific labels (e.g.,
  only SSD nodes, only GPU nodes)
- **Taints and tolerations:** DaemonSets automatically tolerate certain taints
  (like `node.kubernetes.io/not-ready`) to start before nodes are fully ready
  for application traffic

## DaemonSet vs Deployment

| Feature       | Deployment                              | DaemonSet                            |
|---------------|-----------------------------------------|--------------------------------------|
| Scaling       | Defined by `replicas: X`                | Defined by node count                |
| Placement     | Scheduler picks best nodes by resources | One pod per node (unless filtered)   |
| Use case      | Web apps, APIs, microservices           | Monitoring, logging, networking      |
| Node addition | No new pods unless manually scaled      | Pod automatically starts on new node |

## Update Behavior

DaemonSets use RollingUpdate by default:

1. Terminate one DaemonSet Pod on a node
2. Wait for the new version to become Ready
3. Move to the next node

This keeps infrastructure services available across the cluster during updates.

## Example Manifest

A Fluentd logging agent running on every node:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      containers:
        - name: fluentd-elasticsearch
          image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
```

## Related

- [Deployments](deployments.md) - For applications with explicit replica counts
