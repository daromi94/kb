# Load test planning

Load testing subjects a system to a defined, realistic level of
concurrent demand to verify it meets performance requirements before
facing real traffic. Workload shape, environment, duration, and
metrics all follow from the question the test is designed to answer.

## What to measure

A load test produces four categories of data:

- **Throughput** — sustained requests per second at the target
  workload.
- **Latency distribution** — response times at p50, p95, p99, and
  p999. Averages hide tail latency — percentiles expose it.
- **Resource utilization** — CPU, memory, network I/O, disk I/O,
  connection pools, thread pools, GC pressure. These are leading
  indicators: they move before throughput or error rate does.
- **Error rate** — fraction of requests that fail, time out, or
  return degraded responses.

## Workload modeling

Identical requests against a single endpoint bypass every contention
path that matters in production. A representative workload must
include the actual read/write ratio, varying payload sizes, cache
hit/miss distribution, think time between actions, and session state.
Randomize inputs enough to defeat caching layers.

### Open vs closed model

A closed-model generator uses a fixed pool of virtual users that wait
for each response before sending the next request. When the target
slows, arrival rate drops — the generator backs off exactly when it
should be pushing harder, hiding saturation.

An open-model generator sends requests at a fixed rate regardless of
response time. This matches how real clients behave and is the only
way to get honest latency numbers under load.

**Coordinated omission.** A generator that slows its send rate while
waiting for slow responses produces an optimistic latency distribution
— the worst-case times are systematically omitted. Any generator that
claims open-model support should be validated against this failure
mode.

## Environment and measurement

Match production topology: node count, instance sizing, network
layout. Contention patterns, coordination overhead, and network
effects on a single box bear no relation to a multi-node cluster.
When full replication is impractical, document the reduced setup so
subsequent runs use the same baseline.

Measure from outside the system under test. Server-side
instrumentation captures server-side latency. Client-side latency
includes TCP handshake, TLS negotiation, load balancer queueing, and
network RTT — this is what users experience.

## Execution

Ramp load in discrete steps rather than jumping to peak. Start below
typical usage to establish a baseline, increase in increments with
holds long enough for metrics to stabilize, then push past the
expected ceiling to find the degradation threshold. Observe whether
the system sheds load gracefully or collapses.

Stepped progression produces multiple data points per run, making it
straightforward to correlate the onset of degradation with a specific
load level — but a single run is still just a data point.

### Baselines

Establish a performance baseline and compare against it across runs.
For systems with performance requirements, load tests belong in CI/CD
to catch regressions before they reach production.

## Observability

Track the four golden signals throughout every test:

- **Latency** — response time distribution as concurrency increases.
- **Traffic** — demand level the generator is injecting.
- **Errors** — timeouts, deadlocks, 5xx responses that only manifest
  under concurrency.
- **Saturation** — how close each resource is to its limit.

Look beyond host CPU and memory. Inter-service network bandwidth may
saturate before compute does. The load generator itself may become the
bottleneck — a single machine often lacks the capacity to stress a
well-tuned target, requiring distributed generation.

### Failure patterns

The interesting failures are subtle. p99 climbing while p50 holds
flat indicates queueing. Periodic GC pauses drive latency spikes at
regular intervals. Connection pool exhaustion produces cliff-edge
failures at a specific concurrency level. Thread pool saturation
cascades into upstream timeouts. A downstream dependency may
bottleneck before the service under test does.

## Related

- [Load test types](load-test-types.md) - Performance test taxonomy
- [Load test implications](load-test-implications.md) - Cost, bandwidth, third-party concerns

---

Return to [Testing](_index.md)
