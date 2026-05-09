# Backpressure

Backpressure is a feedback mechanism where a downstream component
signals to an upstream component that it cannot keep up, causing
the upstream to slow down, buffer, shed load, or reroute. It makes
the rate mismatch between producers and consumers explicit so the
system can respond before it collapses.

## The problem it solves

In any producer-consumer pipeline, the producer's natural rate is
rarely the same as the consumer's processing rate. Without a
feedback channel, a fast producer feeding a slow consumer leads to
unbounded queue growth, memory exhaustion, GC pressure, latency
spikes, and cascading failure as timeouts propagate and retries
amplify load.

Queues hide the imbalance until they don't. Backpressure exposes
it and propagates it upstream while there is still time to act.

## Mechanisms

**Blocking / pull-based flow control.** The consumer pulls work
when ready. A bounded blocking queue is canonical: when full, the
put operation blocks the producer. Stream APIs formalize this with
explicit demand — the subscriber tells the publisher how many items
it can accept, and the publisher never sends more. TCP's sliding
window is the same idea at the transport layer: the receiver
advertises a window size, and the sender cannot exceed it.

**Credit-based schemes.** The consumer hands out credits; the
producer spends one per message and stops when it runs out. This
generalizes well across network boundaries because credits can be
batched and refilled asynchronously.

**Rate limiting and admission control.** When signals cannot
propagate all the way back — for example, when the producer is an
external client — reject or throttle at the edge. Token buckets,
leaky buckets, and concurrency limiters fall here. Backpressure is
expressed as 429s, queue rejections, or rising latency that clients
are expected to interpret.

**Load shedding.** When buffers fill and the producer cannot be
slowed, drop work — preferably the lowest-priority work, and
preferably early. Head-drop (drop the oldest) beats tail-drop (drop
the newest) under sustained overload, since the oldest work is most
likely past its deadline.

## Principles

*Bounded everything.* Unbounded queues are the most common source
of mysterious outages. Every buffer, thread pool, connection pool,
and channel should have a finite capacity, and the behavior at
capacity should be a deliberate design decision rather than a
default.

*Propagate end-to-end.* If service A pushes back on service B but
B's upstream load balancer keeps accepting connections, the
pressure just relocates to a different buffer. The signal needs a
path all the way to whatever can actually slow down or reject.

*Latency is a backpressure signal too.* Little's Law says that if
arrival rate exceeds service rate, queue length grows without bound
and so does latency. Rising p99 latency with stable throughput is
often the first observable symptom that a system is at its capacity
ceiling. Using latency as the control signal directly is more robust
than measuring queue depth.

*Retries without backpressure amplify load.* A struggling service
that returns errors will see clients retry, multiplying the load it
cannot handle. Retries need budgets, jitter, and circuit breakers
— themselves a coarse form of backpressure.

## Network of queues

A distributed system is a network of queues. Stability requires
that every queue has a way to say "no" or "slow down" to whatever
feeds it. Backpressure is the name for that signal.

## Related

- [CoDel](codel.md) - Time-based load shedding
- [Metastable failures](metastable-failures.md) - Self-sustaining failure states
- [Blast radius reduction](blast-radius-reduction.md) - Containment through compartmentalization

---

Return to [Concepts](_index.md)
