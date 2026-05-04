# Shared memory illusion

Shared memory is an abstraction that no longer reflects how hardware
works. CPUs communicate by shipping cache lines, which is fundamentally
message passing.

## CPU caches hide memory

CPUs write to cache lines, not to main memory directly. Most caches are
local to a core — writes by one core are invisible to another until the
cache line is explicitly shipped to the other core's cache via the cache
coherence protocol.

```text
Core A              Core B
+----------+        +----------+
| Cache L1 |        | Cache L1 |
|  [x = 5] |        |  [x = ?] |
+----+-----+        +----+-----+
     |  cache line ship  |
     +-------->>---------+
```

## The cost of visibility

On the JVM, cross-thread visibility requires volatile markers, Atomic
wrappers, or locked sections. Marking all variables volatile is not
viable — shipping cache lines across cores stalls the involved cores
and creates bottlenecks on the coherence protocol. The slowdown is
orders of magnitude.

Even for experienced developers, deciding which locations need volatile
or which atomic structures to use is error-prone.

## Message passing is the reality

Inter-CPU communication and network communication are more alike than
they appear. In both cases, data moves explicitly between independent
entities. Shared memory just hides this.

The principled approach: keep state local to each concurrent entity and
propagate data between them through explicit messages. This is exactly
what the actor model does — and it aligns with how the hardware actually
works.

## Related

- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - The OOP argument for actors
- [Message passing](message-passing.md) - Communication model aligned with hardware

---

Return to [Pekko](_index.md)
