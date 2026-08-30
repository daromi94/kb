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

Queues temporarily conceal the imbalance by accumulating work.
Backpressure turns the mismatch into a signal that upstream components
can use to reduce demand.

## Mechanisms

Every mechanism closes the same loop: work moves downstream, while a
capacity signal moves upstream.

```text
+-------------------+      work       +---------------------+
| Upstream producer | --------------> | Downstream consumer |
+-------------------+                 +----------+----------+
          ^                                      |
          |           capacity signal            |
          +--------------------------------------+
```

The signal matters only if the upstream component changes its behavior.
It may send less work, wait, reroute, or reject new work.

**Demand-driven flow control.** The consumer requests work when ready.
Stream protocols formalize this with explicit demand: the consumer
tells the producer how many items it can accept, and the producer does
not exceed that amount.

**Blocking flow control.** A bounded blocking queue makes the producer
wait when the queue is full. The consumer frees capacity as it removes
work, which allows the producer to continue.

**Credit-based schemes.** The consumer hands out credits; the
producer spends one per message and stops when it runs out. This
generalizes well across network boundaries because credits can be
batched and refilled asynchronously. TCP uses the same principle at
the transport layer: the receiver advertises a window, and the sender
limits the amount of unacknowledged data accordingly.

**Boundary controls.** Rate limiting and admission control are not
backpressure themselves. When a signal cannot reach an external
producer directly, these controls reject or throttle work at the edge.
An overload response becomes a backpressure signal only when the
producer interprets it and reduces demand.

**Load shedding.** When buffers fill and the producer cannot be
slowed, drop low-priority work early. For deadline-bound work under
sustained overload, head-drop can outperform tail-drop because the
oldest work is most likely past its deadline.

## Principles

**Bound every point of accumulation.** Unbounded queues silently
absorb load until the system collapses. Every buffer, thread pool,
connection pool, and channel should have a finite capacity. Its
behavior at capacity should be a deliberate design decision.

**Propagate end to end.** If service B pushes back on service A but
the gateway in front of A keeps accepting requests, the pressure
relocates to the gateway's queue:

```text
Forward work:

+--------+    +---------+    +-----------+    +-----------+
| Client | -> | Gateway | -> | Service A | -> | Service B |
+--------+    +---------+    +-----------+    +-----------+

Pressure signal:

+--------+    +---------+    +-----------+    +-----------+
| Client | <- | Gateway | <- | Service A | <- | Service B |
+--------+    +---------+    +-----------+    +-----------+
```

The signal must reach the component that can slow down or reject new
work. Otherwise, overload merely moves to another queue.

**Latency can serve as a control signal.** If arrival rate exceeds
service rate, queue length and latency grow without bound. Rising
99th-percentile (p99) latency with stable throughput often reveals
that a system has reached its capacity ceiling. If the producer
observes that latency and reduces demand, the measurement carries
pressure upstream. Latency can be more useful than queue depth when
work items have different processing costs because it measures the
delay that the system actually creates.

**Retries without backpressure amplify load.** Errors often cause
clients to retry, multiplying the load on a struggling service.
Retries need budgets and jitter. Circuit breakers contain repeated
failures; when their rejections cause callers to reduce demand, they
also help carry a pressure signal upstream.

## Network of queues

A distributed system is a network of queues. Stability requires
that every queue has a way to say "no" or "slow down" to whatever
feeds it. Backpressure is the name for that signal.

---

Return to [Concepts](_index.md)
