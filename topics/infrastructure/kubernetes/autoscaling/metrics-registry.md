# Metrics registry

The HPA does not read metrics from Pods directly. It reads them through
extension APIs served by the Kubernetes API server — together called the
metrics registry. Any metric that drives autoscaling must be exposed
through one of these APIs.

## The three metric APIs

| API              | Group                     | What it serves                                 |
|------------------|---------------------------|------------------------------------------------|
| Resource Metrics | `metrics.k8s.io`          | CPU and memory for Pods and Nodes              |
| Custom Metrics   | `custom.metrics.k8s.io`   | Arbitrary metrics tied to a Kubernetes object  |
| External Metrics | `external.metrics.k8s.io` | Arbitrary metrics unrelated to cluster objects |

The Resource Metrics API is fixed to CPU and memory; it cannot be
extended. Use Custom or External for anything else.

Custom vs External is about association. A request rate per Pod is a
custom metric (associated with a Pod). An SQS queue depth that happens
to drive scaling decisions is external (no cluster object owns it).

## Collectors and API servers

Each metric API is served by a **metric API server** registered as an
APIService with the Kubernetes API server. Behind each API server is a
**metrics collector** that gathers raw data from the actual sources.

| API              | Collector             | API server         |
|------------------|-----------------------|--------------------|
| Resource         | cAdvisor (in kubelet) | Metrics Server     |
| Custom, External | Prometheus            | Prometheus Adapter |

cAdvisor is embedded in the kubelet, so the collector side of the
Resource Metrics pipeline is already running on every node. The API
server side (Metrics Server) is not installed by default.

Other vendors ship their own collector/adapter pairs (Datadog, Google
Cloud Monitoring, etc.) that register the same API groups.

## Custom metric pipeline

End-to-end, a per-Pod request-rate metric reaches the HPA like this:

```
+---------------------+
|   Application Pod   |
|  /metrics endpoint  |
+----------+----------+
           | scrape
           v
+---------------------+
|     Prometheus      |
|  time series store  |
+----------+----------+
           | PromQL
           v
+---------------------+
| Prometheus Adapter  |
|    serves Custom    |
|     Metrics API     |
+----------+----------+
           | GET
           v
+---------------------+
|   Kubernetes API    |
|       server        |
+----------+----------+
           | query
           v
+---------------------+
|   HPA controller    |
+---------------------+
```

Setup is four steps:

1. Instrument the app to expose a counter (e.g., total requests) on a
   `/metrics` endpoint.
2. Deploy Prometheus and configure it to scrape the app's Pods.
3. Deploy Prometheus Adapter with a rule that turns the counter into a
   per-second rate via PromQL (e.g., `rate(http_requests_total[1m])`)
   and exposes it as `myapp_requests_per_second` under the Custom
   Metrics API.
4. Create a HorizontalPodAutoscaler referencing that metric name.

## Related

- [Horizontal Pod Autoscaler](horizontal-pod-autoscaler.md) - The client of the metrics registry
- [Autoscaling types](autoscaling-types.md) - HPA in context

---

Return to [Autoscaling](_index.md)
