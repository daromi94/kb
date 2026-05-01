# Architectural lessons

Trino's design choices reflect deliberate tradeoffs that have aged
well in production. The lessons below are transferable principles,
not Trino-specific mechanics.

## Separate what changes at different rates

Compute, storage, and metadata change on different timescales. Trino
keeps them as fully separate concerns: data lives in object stores or
source databases, metadata lives in catalogs, and compute is
ephemeral. You can scale workers without touching data, swap storage
formats without touching the engine, and replace the metastore
without losing data.

Identify the axes along which a system needs independent evolution
and put hard interfaces between them. The cost is real — a federated
join across two sources is slower than the same data colocated in one
engine — but the flexibility unlocks elasticity that tightly coupled
systems cannot match.

## Narrow plugin interfaces beat rich ones

The connector SPI is small. A connector implements a handful of
interfaces — for metadata, splits, and page sources — and almost
everything else lives in the engine. Most of what makes Trino useful
is the third-party ecosystem written against this surface.

The lesson is not "have a plugin system." It is that the surface area
of the interface determines who can extend the system and how stable
extensions are over time. A bloated SPI that exposes internal types
makes every refactor break every plugin; a narrow SPI that hides
internals lets the core evolve while extensions keep working. The
deeper version: getting the line right between "what the engine knows
generically" and "what is source-specific" is mostly what makes a
federation engine work.

## Centralize what is genuinely hard

The coordinator is a single point of failure and a bottleneck. Trino
accepts this rather than fighting it. Planning, optimization,
scheduling, and admission are genuinely hard to distribute correctly:
they need consensus, raise split-brain risks, and depend on
consistent metadata views. The workload — queries lasting seconds to
minutes — does not demand it. Workers, by contrast, are nearly
stateless and trivially scalable.

Don't reflexively distribute everything. Identify which parts of the
system genuinely need distribution for the workload, and centralize
the rest where it is simpler and faster. Distributed consensus is
expensive — if you can avoid needing it, avoid it.

## Match the consistency model to the workload

Trino is eventually consistent about cluster membership. A new worker
takes seconds to become schedulable; a dead worker takes up to ~30
seconds to fall out. For an analytics engine running multi-second
queries, this is invisible. For a low-latency RPC mesh, it would be
unusable.

Pick the weakest consistency model that satisfies the workload's
actual needs. Trino's discovery layer is straightforward code because
it does not have to be strongly consistent. The same problem under
strong consistency requirements becomes etcd or ZooKeeper — orders
of magnitude more code, operational burden, and failure modes.

## Backpressure is a system property, not a feature

Trino's flow control is not a single mechanism — it emerges from many
local decisions. Operators block when memory is unavailable. Drivers
yield when their output buffer is full. The split scheduler only
sends work as workers report capacity. Load distributes to available
resources without any central rate limiter.

In a pipelined system, backpressure is what keeps queues bounded and
latency predictable. The cure is making "I can't take more right now"
a first-class signal at every boundary, with producers respecting it.
Adding it after the fact is brutal — every component has to learn to
block, every queue has to grow a backpressure signal, every test has
to verify it. Build it in from the start.

## Make races safe, not impossible

Trino's query state machine has exactly one place where state
transitions happen, with atomic compare-and-set, and terminal states
are absorbing. Failures, cancellations, and timeouts all funnel
through the same call. Worker death, client disconnect, memory limit,
and SQL error can race; whichever lands first wins, the rest become
no-ops.

Distributed systems with independent failure detectors and async
communication cannot prevent races. The pattern is not to prevent
them — it is to make them safe. Idempotent state transitions,
monotonic state machines, and compare-and-set at the boundary mean
the cleanup logic does not need to know who killed the query, just
that something did.

## Polling protocols are underrated

Trino's wire protocol is HTTP polling. Clients poll for results. The
coordinator polls workers for task status. Workers heartbeat to the
discovery service. There are no persistent streaming connections, no
callbacks, no push notifications.

Polling looks primitive next to streaming protocols, but it composes
beautifully. Load balancers handle it without configuration; firewalls
do not choke; network blips are absorbed by the next poll. State
lives in HTTP requests rather than connection objects, so a
coordinator restart does not drop everything mid-flight. Push
protocols feel cleaner but couple liveness to connection state, and
that coupling is where bugs live.

## Put the optimization budget where it matters

The optimizer is large and slow — the coordinator can spend hundreds
of milliseconds planning a complex query. But that work is amortized
over a long execution where the savings dwarf the planning cost. A
predicate pushdown that turns a ten-minute scan into a ten-second
scan is worth a 200-millisecond planner pass.

The worker hot path, by contrast, is brutally optimized: per-query
bytecode generation, columnar pages so loops vectorize, careful
avoidance of allocation in inner loops. Operators run billions of
times; planners run once. Identify which code paths run at which
rates and spend your optimization budget accordingly. Most systems
get this backwards — heavy frameworks in the hot path, sloppy logic
at the boundaries.

## Decouple speed and resilience at the right seam

Pipelined execution is fast and fragile. Materialized execution is
slow and resilient. Trino chose pipelined, lived with the fragility
for years, then added fault-tolerant execution as an alternative mode
that reuses the same query state machine, the same operators, the
same connectors — only the exchange layer changes.

When there is a fundamental tradeoff between speed and resilience, do
not pick once for the whole system. Build the engine so the choice
can be made per-workload. The interface that made this possible was
the exchange seam: pipelined and spooled exchanges implement the same
contract, so the rest of the engine does not care which is in use.
Identifying the right seam in advance is hard; if you do it well, you
get to make big changes later without big rewrites.

## Operational simplicity through fewer dependencies

Trino has no coordination service of its own, no storage layer, no
daemon to babysit. A cluster is one coordinator and N worker JVMs
sharing a config directory. It runs in Kubernetes, on bare metal, on
a laptop, with the same model.

Every external dependency is a permanent operational tax — version
mismatches, network partitions, capacity planning, on-call burden.
Internalizing the small dependencies (embedded discovery, no
persistent metadata of its own, ephemeral state only) makes the
system harder to break and easier to operate. Some dependencies are
worth paying for; the default should be to do without and prove the
dependency earns its keep.

## A system is the constraints it accepts

Trino accepts that it is an analytics engine, not a transactional
database; that it runs as a cluster of cooperating processes, not a
single distributed service; that planning is centralized, execution
distributed, storage external. Inside those constraints it is a
remarkably coherent piece of engineering. Outside them, it is the
wrong tool.

Most architectural failure comes from systems trying to be everything.
Most architectural success comes from systems that pick their
constraints early and hold them.

## Related

- [Architecture](architecture.md) - Coordinator, workers, and connectors
- [Connector API](connector-api.md) - The SPI in practice
- [Backpressure](backpressure.md) - Self-regulating flow control
- [Query termination](query-termination.md) - Idempotent state transitions
- [Fault-tolerant execution](fault-tolerant-execution.md) - The exchange seam
- [Discovery service](discovery-service.md) - Eventually consistent membership

---

Return to [Trino](_index.md)
