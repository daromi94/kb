# Load test implications

Load tests at scale produce side effects that can invalidate results
or drive unexpected costs.

## Cost

Deploying many servers for long-running tests consumes significant
compute and bandwidth. Model the target system carefully — a smaller
representative setup can produce valid results at a fraction of the
cost. Set billing alerts on the services under heaviest load before
the first run.

## Third-party dependencies

Calling external services during a test consumes their quotas, incurs
their costs, and introduces uncontrolled variables. A slow third party
creates back pressure that skews latency numbers. An unavailable one
injects false errors unrelated to your system.

Replace external calls with locally-hosted stubs returning fake but
valid responses. This isolates your system's performance from factors
outside your control.

## Test data accumulation

High-volume tests generate large amounts of metric and log data.
Time-series databases, object stores, and local disk all need
capacity planning. Define partitioning and retention policies before
the first run to avoid storage becoming a bottleneck or cost surprise.

## Network bandwidth

The load generator typically has fewer machines than the target
cluster, so each generator instance must push disproportionate
traffic. If upload bandwidth on the generator saturates, the test
measures the generator's limits, not the application's. Size generator
instances accordingly and choose instance types with enhanced
networking.

## Related

- [Load test planning](load-test-planning.md) - Environment and measurement setup

---

Return to [Testing](_index.md)
