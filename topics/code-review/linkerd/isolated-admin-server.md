# Isolated admin server

Run the admin interface on a separate thread with its own event loop,
giving operators a control plane into the service without touching the
data path.

## How Linkerd2-proxy does it

The admin server runs on a dedicated thread, independent of the
proxy's main runtime. It exposes:

| Endpoint                         | Purpose                                    |
|----------------------------------|--------------------------------------------|
| `GET /live`                      | Liveness — always 200                      |
| `GET /ready`                     | Readiness — 200 once identity is certified |
| `GET /metrics`                   | Prometheus metrics from all subsystems     |
| `GET/PUT /proxy-log-level`       | Read or change tracing filter at runtime   |
| `GET /logs.json`                 | Stream structured logs as JSON             |
| `GET /env.json`                  | Dump environment variables as JSON         |
| `POST /shutdown`                 | Trigger graceful drain via HTTP            |
| `GET /debug/pprof/profile.pb.gz` | CPU profiling in pprof format              |

Sensitive endpoints are localhost-only; public endpoints like
liveness and readiness are open for kubelet probes and Prometheus
scrapers.

## Why it works

Isolating admin from the data path means operators can always
inspect a sidecar regardless of proxy load. A saturated event loop
still responds to liveness checks, so Kubernetes can distinguish
"overloaded" from "dead." Runtime log-level changes and log
streaming let you debug a misbehaving sidecar without restarting the
pod and losing the reproduction. The shutdown endpoint gives the
control plane an HTTP alternative to SIGTERM. The pprof endpoint
lets you profile in production without attaching a debugger.

## Takeaway

When a service has both a data path and an operational interface,
run them on separate execution contexts. The admin path must never
compete with the data path for resources. This is what makes
liveness checks trustworthy — if admin shares the same event loop
as request processing, a saturated loop makes the process appear
dead to the orchestrator even when it is not.

## Related

- [Cooperative drain shutdown](cooperative-drain-shutdown.md) - Shutdown signaling
- [Structured config loading](structured-config-loading.md) - Startup discipline

---

Return to [Linkerd2-proxy](_index.md)
