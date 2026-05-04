# Actor best practices

Rules for writing well-behaved actors: process events efficiently,
don't hog resources, and respect the actor model's boundaries.

## Don't block

Actors must not passively wait while occupying a thread. No blocking
on locks, network sockets, or other external entities. Process events
and generate responses in an event-driven manner. When blocking is
truly unavoidable, isolate it with dedicated dispatchers.

## Keep messages immutable

Never pass mutable objects between actors. Exposing mutable state
through messages breaks actor encapsulation and drops you back into
shared-memory concurrency with all its hazards. Prefer immutable
message types.

## Don't send behavior in messages

Actors are containers for behavior and state. Resist sending closures
or functions within messages — even though Scala makes it tempting.
Closures can capture mutable state from the enclosing actor, silently
sharing it with the recipient and breaking the actor model's
guarantees.

## Related

- [Message passing](message-passing.md) - How actors communicate
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - Why OOP breaks under concurrency
- [Hierarchical design](hierarchical-design.md) - Structuring actor hierarchies

---

Return to [Pekko](_index.md)
