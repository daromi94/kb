# Rainbow deployments

A release strategy where each new version ships as a brand-new
Deployment instead of modifying the existing one. Old Deployments
keep running until their workload drains — long-lived connections
close, long-running jobs finish — then they are removed. The name
comes from the image of many version-colored Deployments coexisting
during the drain window.

## When to use

- **Long-lived connections.** WebSockets, server-sent events, gRPC
  streaming. Clients should disconnect on their own schedule, not
  when a pod's grace period expires.
- **Long-running jobs.** Video transcoding, batch processing,
  training runs. A rolling update would kill in-flight work, and
  setting `terminationGracePeriodSeconds` to hours brings its own
  problems.

For standard request/response services, a rolling update on a single
Deployment is simpler and strictly better.

## Why not just increase the grace period

Stretching `terminationGracePeriodSeconds` to hours has three
cluster-wide costs:

- **Metrics gap.** Pods are dropped from their EndpointSlice the
  moment they enter Terminating. Prometheus stops scraping them,
  so the grace-period window produces no observability.
- **Mixed-version logs.** Running and Terminating pods of different
  versions share the same workload name, muddling logs and traces.
- **No liveness check.** The kubelet does not run liveness probes
  during termination, so a stuck process is never restarted.

Running each version as its own self-contained Deployment sidesteps
all three.

## Draining the old version

Once the old Deployment's workload is done:

- **Manual delete** — the operator removes it when confident the
  drain is complete.
- **Scale-to-zero autoscaler** — controllers like KEDA watch a
  metric (queue depth, active connections) and scale the Deployment
  to zero when the metric reaches zero.

## Trade-offs

- Extra replicas during the overlap window, and ongoing cost of
  keeping old Deployments alive until their clients drain.
- Version-tagged Deployment names and Service selectors that must
  route correctly across coexisting versions.
- Cleanup discipline — without it, old Deployments accumulate
  indefinitely.
- Blue/green and canary are simpler when you don't need overlap for
  draining.

---

Return to [Best practices](_index.md)
