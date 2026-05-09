# Reliability

The Linkerd proxy applies three reliability techniques transparently
to every request it carries: load balancing, retries, and timeouts.
Failures the proxy can absorb (retried, timed out, rerouted) never
reach the application.

## Load balancing (EWMA)

Linkerd load-balances requests across the endpoints of a service using
an **exponentially weighted moving average** of recent response times.
Each endpoint carries a score that blends its latency history,
weighting recent samples more heavily than old ones.

The score decays over time, so a short spike does not permanently
penalize an instance, but sustained slowness quickly shifts traffic
to faster peers. The effect is implicit outlier detection: a slow or
saturated pod simply receives less traffic, with no health-check
threshold to tune by hand.

For opaque TCP, where request boundaries are invisible, the proxy
balances new **connections** across endpoints rather than individual
requests.

## Retries

Failed HTTP calls can be retried automatically when the route is
marked as safe (idempotent). Retries happen entirely inside the proxy
and are enforced against a **retry budget** — a bound on how many
extra attempts may be issued relative to the base request rate.
The budget prevents a failing dependency from amplifying load on
itself through a storm of retries.

## Timeouts

Per-route timeouts bound how long the proxy will wait for a response
before failing the call back to the client. This protects a caller
from having its resources tied up by a slow or hung downstream.

---

Return to [Linkerd](_index.md)
