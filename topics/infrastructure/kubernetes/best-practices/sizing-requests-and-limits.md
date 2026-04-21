# Sizing requests and limits

Guessing at request and limit values is unreliable — too low causes
OOMKills and CPU throttling, too high wastes cluster capacity. The
practical approach is to measure real usage under production-like
load and let the data decide.

## Measure first

Metrics Server collects per-container CPU and memory samples from
the kubelet on every node. Run the workload against realistic load
long enough to capture steady-state and peak behavior.

## Let VPA do the statistics

The Vertical Pod Autoscaler fits a statistical model to the
historical metrics and produces three recommendations per container:

| Recommendation | Meaning                                        |
|----------------|------------------------------------------------|
| lowerBound     | Below this, the container is likely to starve  |
| target         | Recommended steady-state value                 |
| upperBound     | Above this, the container is likely overscaled |

Run VPA in **recommendation-only mode** (`updateMode: "Off"`) so it
publishes values on the VPA object without mutating the workload.
Read them with `kubectl describe vpa`.

## Map recommendations to the manifest

- **target → requests** — what the container typically needs, so the
  scheduler reserves that much
- **upperBound → limits** — the ceiling before the container is
  throttled (CPU) or killed (memory)

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## Re-measure periodically

Applications drift. Code changes, traffic patterns evolve, and the
numbers that were right six months ago are no longer right. Treat
sizing as an ongoing loop — not a one-time setup.

---

Return to [Best practices](_index.md)
