# cAdvisor

cAdvisor (Container Advisor) is an open-source daemon from Google that
collects and exports resource-usage metrics for running containers. It
runs on the host, not inside containers, and discovers containers
automatically via cgroup events.

## What it collects

Per-container and machine-wide metrics read directly from Linux kernel
interfaces (cgroups, `/proc`, `/sys`):

- CPU — usage, throttling, per-CPU breakdown, load
- Memory — usage, working set, limits
- Network — bytes and packets per interface, errors
- Filesystem and disk I/O

## How it exposes data

- Web UI at `http://host:port/` with per-container dashboards
- Versioned REST API under `/api/`
- Prometheus scrape endpoint at `/metrics`

## Role in Kubernetes

Embedded in the kubelet on every node. The kubelet surfaces
cAdvisor-collected stats on its own API, which Metrics Server scrapes
and aggregates to serve the cluster-wide Resource Metrics API.

cAdvisor can also run standalone (binary, container, or DaemonSet)
when a richer per-container view than the Resource Metrics API
provides is needed.

---

Return to [Autoscaling](_index.md)
