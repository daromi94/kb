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

## State

An actor's state — a state machine, a counter, a set of listeners,
pending requests — is what makes it valuable. Single-threaded message
processing protects this state without locks: no other actor can read
or write it, and only one message is handled at a time.

## Behavior

A behavior is the function that defines how an actor reacts to each
message. It may change over time — either through state variables
that the function reads, or by returning a different function to
handle the next message. On restart, the actor reverts to its initial
behavior.

Behaviors are typed to match their actor ref. A successor behavior
must handle the same message type as its predecessor, preserving the
validity of all outstanding references.

## Related

- [Message passing](message-passing.md) - How actors communicate
- [Actor lifecycle](actor-lifecycle.md) - Actor creation and termination
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - Why OOP breaks under concurrency
- [Hierarchical design](hierarchical-design.md) - Structuring actor hierarchies
- [Supervision](supervision.md) - Parent-child fault handling

---

Return to [Pekko](_index.md)
