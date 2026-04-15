# Failure modes

Every system has a bottleneck. The point of a load test is not to
learn *that* the system breaks, but *how*. Two systems with the same
throughput ceiling can fail in radically different ways, and the
difference decides whether overload becomes a brief slowdown or a
full outage.

## Graceful versus catastrophic

| Graceful failure | Catastrophic failure |
|------------------|----------------------|
| Backpressure     | Cascading timeouts   |
| Load shedding    | Retry storms         |
| Bounded queues   | Thundering herds     |

**Graceful** modes contain the damage. Backpressure pushes the
overload upstream so the slowest stage paces the system. Load
shedding drops requests at the edge before they consume capacity
downstream. Bounded queues absorb short bursts and refuse the rest.
The service stays up; latency or error rate degrades in a controlled,
recoverable way.

**Catastrophic** modes amplify the damage. Failure spreads faster
than capacity can recover, and the system collapses well below the
throughput it could sustain in steady state. The patterns below all
share that signature — a small disturbance becomes a system-wide
outage.

## Catastrophic patterns

**Congestion collapse.** Throughput actually *decreases* past a
certain load. The system spends more cycles on overhead — context
switching, lock contention, GC, retries — than on useful work.
Pushing harder yields less. Recovery often requires shedding load
entirely until the system unwinds.

**Retry storms.** Service A calls B; B slows; A times out and
retries; the retries multiply load on B; B slows further. B ends up
drowning in retries of requests whose original callers gave up
long ago. Defenses: exponential backoff, jitter, retry budgets,
circuit breakers. Reproduce in a load test by deliberately slowing
a dependency and watching what the caller does.

**Thundering herd.** Many clients react to the same event — a cache
expiring, a service recovering, a scheduled job firing — and hit a
backend simultaneously. The canonical case is cache stampede: a
popular key expires, a thousand requests miss at once, all thousand
hit the database, the database falls over. Defenses: single-flight
request coalescing, probabilistic early expiration, jittered TTLs.

**Queue buildup.** A system accepts work faster than it processes
it. Queues grow, latency for queued items grows with them, and by
the time a request is handled its caller has timed out. The tell:
latency keeps climbing while throughput has plateaued. The fix is
bounded queues with explicit rejection, not unbounded queues that
pretend to absorb everything.

**Head-of-line blocking.** One slow item stalls everything behind
it. A slow query holding a connection, a slow client draining a
response, a slow handler blocking an event loop — all the same
shape. The fix is isolation: separate pools per workload, timeouts
everywhere, async I/O where appropriate.

**Resource leaks.** File descriptors, connections, memory, threads.
A leak of one per request is invisible in functional tests and
fatal in a soak test, where hours of sustained load expose what a
short run cannot.

## Watch the server, not just the client

Client-side metrics show *that* the system slowed down. They cannot
show *why*. A latency spike must be correlated with what is happening
on the server at the same moment — a connection pool saturating,
garbage collection pausing, a queue backing up. Without that
correlation a load test yields a number with no diagnosis attached,
and the next regression has nothing to point at.

## Related

- [Bottlenecks](bottlenecks.md) - What runs out and forces the failure
- [Saturation curve](saturation-curve.md) - The phases the failure plays out across
- [Performance signals](performance-signals.md) - Server-side metrics to correlate
- [Performance testing](performance-testing.md) - The discipline this fits inside

---

Return to [Testing](_index.md)
