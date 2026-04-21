# Metastable failures

A metastable failure is a bad state that persists after the trigger
that caused it has gone away, because the system's own normal
behavior now sustains the failure. The dashboards still look healthy
— CPU is busy, requests are flowing — but useful work has stopped.
The system is stable in a place no one wants it to be.

## Trigger vs sustaining loop

Every metastable failure has two parts. A **trigger** — a brief
spike, a partial network blip, a deploy gone slightly wrong — knocks
the system off its normal operating point. A **sustaining feedback
loop** then keeps it there. The trigger is a spark; the loop is the
fuel.

Many different triggers can land the system in the same metastable
state, so chasing the trigger as a root cause is a treadmill: you
fix yesterday's spark and tomorrow's spark finds the same fuel. The
disease is the loop. Treating the loop is the only intervention that
actually prevents recurrence.

## High throughput, zero goodput

The signature of a metastable failure is a system that is busy but
producing nothing useful. Throughput — requests served, CPU
consumed, packets moved — looks normal or even high. **Goodput** —
work whose result reaches a client that still cares — is zero,
because clients have already timed out and moved on by the time
their response is ready.

When a service is up but down, working but broken, the cause is
almost always a sustaining loop, not a dead component. Look for what
is generating the work, not what is failing to handle it.

## How safeguards become amplifiers

The counterintuitive part is that the loop is usually built out of
the mechanisms engineered for normal-day reliability. Retries reduce
the common-case error rate but, under load, they convert a small
outage into a sustained internal storm where each failed attempt
creates more attempts. A 99% cache hit rate is also a 100x load
amplifier the moment the cache cools. A fallback path from a failing
cache to the database can turn a partial degradation into a total
outage by sending every web server's traffic at a database sized
only for cache misses.

The safeguard is not wrong. It is doing exactly what it was designed
to do. The problem is that what works for one request at a time
becomes a cycle when many components do it at once.

## Why this happens at all

Each common-case optimization lets the system run closer to saturation:
slightly larger buffers, slightly more retries, slightly higher
cache dependency, slightly tighter timeouts. Steady-state efficiency
improves, every dashboard turns greener, and the operating point
moves closer to the threshold between the stable region and the
vulnerable one.

Dashboards show every optimization win. They do not show the system
becoming more fragile. The wins accumulate, until a disturbance the
system used to absorb becomes an outage.

## Breaking the loop

Recovery from a metastable failure requires interrupting the
feedback path, not waiting for the trigger to clear. The trigger has
usually been gone for some time. Mitigations that work all act on
the loop itself: shedding load before it queues, capping concurrency
rather than only arrival rate, applying backpressure end-to-end,
adding jitter and budgets to retries, and per-tenant quotas that
stop one workload's spike from recruiting every other workload into
the storm.

## The lesson

When a system is stable but produces nothing, look for the loop, not
the spark. When proposing a change that improves the common case,
ask what margin it consumes and what the new boundary looks like —
the optimization that makes today's graphs greener may be the one
that sustains tomorrow's outage.

## Related

- [Crash or continue](crash-or-continue.md) - Error handling
  decisions that prevent triggers from cascading
- [Blast radius reduction](blast-radius-reduction.md) - Containment
  so one workload's spike cannot recruit the whole fleet

---

Return to [Concepts](_index.md)
