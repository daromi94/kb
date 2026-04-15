# Performance testing

A performance test asks whether a workload's throughput, latency
percentiles, and error rate hold up under realistic load. The answer
is only as useful as four choices made before the test runs: what
counts as pass or fail, how closely the environment matches
production, what load shapes the test covers, and where in the
delivery pipeline the test runs.

## Performance targets are the pass/fail criteria

State the performance targets as **service-level objectives** before
writing any tests. Without them the test can only collect data, not
decide whether the workload is acceptable, and regressions slip
through because nothing in the test is set up to catch them.

Derive the targets from business needs and user expectations, not
from what the current system already does. A baseline-derived target
passes any release that matches current behavior, which is the
opposite of catching drift.

## Match production in the test environment

A test predicts production only to the degree that the test
environment resembles production. Run it against a smaller or
simpler stack and the numbers describe that stack, not the system
that will actually carry the workload. The parts that bite under
load — concurrency patterns, coordination overhead, cache behavior,
network effects — do not scale linearly with cluster size, and a
smaller stack hides exactly the contention paths the test most
needs to exercise.

Use infrastructure as code and container-based deployments so every
run starts from the same environment. The cloud makes
production-scale environments affordable on demand, so the cost
argument for running against a scaled-down stack no longer holds.
When full fidelity is impractical, document the reductions so later
runs share a common baseline and stay comparable.

## Cover the full load envelope

A single load level cannot exercise every failure mode the workload
will encounter. Run the test across the range the production system
will see — average usage, sustained peak, sudden spike, and
deliberately beyond the expected ceiling — because each shape answers
a different question.

Average usage confirms day-to-day SLO compliance. Sustained peak
shows whether the workload holds under the worst reasonable demand.
Spike tests check whether elasticity, load shedding, and circuit
breakers absorb sudden surges without cascading. **Stress tests** —
running past the expected ceiling — reveal the breaking point and
the shape of failure, which no test inside the envelope can produce.

## Treat it as continuous, not a one-off gate

Performance testing belongs in the continuous integration pipeline,
not as a pre-release gate. When each merge is checked against the
baseline, a regression points at the commit that caused it. When
checks wait until release, regressions arrive in bundles and
isolating any one of them means bisecting the whole batch.

Feed production monitoring back into the test suite. Real traffic
reveals which request mixes and which resource behaviors actually
matter. Fold those observations into new test cases, or the suite
slowly drifts away from what production does.

## Related

- [Service level objectives](../sre/service-level-objectives.md) - The targets the tests check against

---

Return to [Testing](_index.md)
