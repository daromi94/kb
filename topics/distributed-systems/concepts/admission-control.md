# Admission control

Admission control is the decision, at a system's edge, whether to
accept a new unit of work — a request, connection, transaction, job
— based on whether the system can actually serve it within its
constraints. Rejected work is dropped fast, before it consumes
resources that committed work depends on.

## Why it exists

A system has a peak throughput at which it completes the most work.
Push it past that peak and throughput does not stay flat — it
collapses.

Every accepted request consumes CPU, memory, locks, connections,
and downstream calls before it finishes — even ones that ultimately
fail. Past the peak, the system spends more resources on doomed
work than on succeeding work, and goodput (successful throughput)
drops toward zero even as offered load keeps climbing.

Admission control refuses the requests that would push the system
past its peak, keeping it in the regime where work actually
completes.

## Versus backpressure

Backpressure is a conversation between connected components about
pacing. Admission control is a unilateral decision at a boundary:
this request, yes or no, right now.

They compose. A service typically uses backpressure signals from its
dependencies as inputs to its own admission decisions at the edge.

## Budgets

The decision can be made against several kinds of budgets:

- **Concurrency.** Cap in-flight requests; the N+1th is rejected or
  briefly queued. The most robust signal in practice — it directly
  bounds resource consumption regardless of request mix. Adaptive
  variants — TCP Vegas-style algorithms — infer the right N by
  watching latency: when latency rises above baseline, the limit
  shrinks; when latency is healthy, it grows. The system finds its
  own capacity. Bounded by Little's Law, $L = \lambda W$.
- **Rate.** Token buckets and leaky buckets cap requests per unit
  time. Useful for fairness and quota enforcement across tenants;
  weaker as overload defense because request cost varies — 1000
  cheap requests and 1000 expensive ones look identical to a rate
  limiter.
- **Resource headroom.** Reject when CPU, memory, queue depth, or
  thread-pool utilization crosses a threshold. Simple to implement
  but brittle: too low and you reject prematurely, too high and the
  system is already in trouble before the threshold trips.
- **Deadlines and queue time.** Drop a request on dequeue if it has
  waited longer than its deadline allows. The client has likely
  already given up; serving it now just steals capacity from
  requests that can still succeed. Often called "LIFO under load"
  — serving the newest first means the oldest (most likely
  abandoned) gets dropped from the tail.

## What to reject

Uniform random rejection is the worst option in multi-tenant
systems — it punishes well-behaved clients alongside abusive ones.
Better schemes prioritize:

- Reject low-priority work first.
- Reject the heaviest users first (weighted fair queuing).
- Reject requests whose deadlines cannot be met.
- Reject by cost class so a flood of expensive requests does not
  starve cheap ones.

Implementations vary — criticality labels, request tags, traffic
classes — but all encode the same idea: critical paths admit first.

## How to reject

The rejection itself must be cheap — a rejected request that costs
as much as a served one defeats the purpose. The response should
communicate intent precisely: HTTP 429 with `Retry-After`, gRPC
`RESOURCE_EXHAUSTED`, or similar, ideally with backoff hints so
clients do not retry immediately into the same rejection.

## Metastable failure

Admission control can create a stable bad equilibrium:

1. A spike pushes the service into rejection.
2. Rejected clients retry.
3. Retries inflate offered load.
4. Inflated load keeps the service in rejection even after the
   original spike has passed.

The system has two stable states — healthy and overloaded — and
once tipped into the bad one, it does not recover on its own.
Defenses: retry budgets (bound retries as a fraction of new
requests), exponential backoff with jitter, and shedding aggressive
enough to actually drain the queue rather than tread water.

## The underlying principle

A system that accepts work it cannot complete is lying about its
capacity, and that lie is paid for in cascading failure. Admission
control is how the system tells the truth at its edges.

---

Return to [Concepts](_index.md)
