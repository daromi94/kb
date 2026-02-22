# Actors

An actor is a lightweight unit of computation that encapsulates state
and behavior. Actors communicate only by exchanging asynchronous
messages — they never share memory or call each other's methods
directly. In practice, each actor:

- Encapsulates private state with no shared mutable data
- Processes one message at a time from its mailbox
- Communicates exclusively through asynchronous message passing
- Can create child actors, forming supervision hierarchies

This eliminates locks and low-level concurrency primitives. The same
code works transparently across local and remote boundaries.

The actor model (Hewitt, Bishop, Steiger, 1973) defines three
fundamental actions an actor may take on receiving a message:

- Send a finite number of messages to actors it knows
- Create a finite number of new actors
- Designate the behavior for its next message

## Design mental model

Think of actors as people in an organization. Assign sub-tasks to
them, arrange their roles into a hierarchy, and define how failures
escalate. This maps directly to supervision trees, message protocols,
and task delegation in code.

## ActorRef

Actors are never accessed directly. Instead, they are represented by
ActorRefs — lightweight handles that can be passed around freely.
The actual actor object is shielded behind the ref — its state,
behavior, mailbox, children, and supervisor strategy are never
directly accessible.

This inner/outer split provides transparency: an actor can be
restarted without updating references elsewhere, moved to a remote
host, or sent messages regardless of where it runs.

ActorRefs are typed. Only messages matching the ref's type parameter
can be sent through it.

## Explicit lifecycle

Actors are not garbage-collected when unreferenced. You must ensure
each actor is eventually terminated to release its resources.

## Related

- [Message passing](message-passing.md) - How actors communicate
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) -
  Why shared mutable state breaks under concurrency
- [Hierarchical design](hierarchical-design.md) - Structuring actor
  hierarchies
- [Supervision](supervision.md) - Parent-child fault handling
- [Actor best practices](actor-best-practices.md) - Rules for
  well-behaved actors

---

Return to [Pekko](_index.md)
