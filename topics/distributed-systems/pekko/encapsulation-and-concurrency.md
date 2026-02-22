# Encapsulation and concurrency

OOP encapsulation guarantees invariant protection only under
single-threaded access. Multiple threads break this guarantee, and
locks are a poor remedy.

## The single-thread assumption

Encapsulation means an object's internal data is only modified through
curated methods that preserve invariants. A binary tree, for example,
exposes operations that maintain sort order — callers rely on this.

This works because a single thread executes each method call to
completion before another begins. The invariant holds between calls,
and each call sees consistent state.

## What breaks under concurrency

When two threads invoke methods on the same object, their instructions
interleave arbitrarily. The encapsulation boundary offers no protection
— both threads read and write internal fields with no coordination.
Invariants are violated silently.

```
Thread A          Object           Thread B
   |--- method() -->|                 |
   |                |<--- method() ---|
   |     interleaved instructions     |
   |       invariant broken           |
```

The mental model of objects communicating via method calls hides the
reality: threads traverse the object graph, and it is threads — not
objects — that drive execution.

## Why locks fail at scale

Locks are the standard fix, but they introduce three problems:

| Problem          | Impact                                          |
|------------------|-------------------------------------------------|
| Limited concurr. | OS must suspend and restore threads — expensive |
| Caller blocking  | Thread cannot do useful work while waiting      |
| Deadlocks        | Multiple locks create circular-wait hazards     |

The result is a no-win situation: too few locks corrupt state, too many
locks kill performance and invite deadlocks.

## Locks do not distribute

Locks work within a single process. Distributed locks require multiple
network round-trips, are orders of magnitude slower, and impose hard
limits on scale-out. Coordinating mutable state across machines via
locking is impractical.

## The case for actors

The actor model sidesteps all of these problems. Each actor:

- Owns its state exclusively — no shared mutable data
- Processes one message at a time — invariants hold between messages
- Communicates only through asynchronous messages — no blocking calls
- Works identically across local and remote boundaries

This eliminates the need for locks entirely, preserves encapsulation
under concurrency, and extends naturally to distributed systems.

## Related

- [Actors](actors.md) - The actor model and its primitives
- [Message passing](message-passing.md) - How actors communicate
  without sharing state
- [Shared memory illusion](shared-memory-illusion.md) - The hardware
  argument for message passing

---

Return to [Pekko](_index.md)
