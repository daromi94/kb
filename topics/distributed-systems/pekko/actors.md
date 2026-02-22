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

## State

An actor's state — a state machine, a counter, a set of listeners,
pending requests — is what makes it valuable. Single-threaded message
processing protects this state without locks: no other actor can read
or write it, and only one message is handled at a time.

Inconsistent state is fatal. When an actor fails, its supervisor
restarts it with fresh state — constructed from scratch, as if
created for the first time. This clean-slate restart is what enables
self-healing: rather than attempting to salvage corrupted state, the
system simply replaces it.

## Behavior

A behavior is the function that defines how an actor reacts to each
message. It may change over time — either through state variables
that the function reads, or by returning a different function to
handle the next message. On restart, the actor reverts to its initial
behavior.

Behaviors are typed to match their actor ref. A successor behavior
must handle the same message type as its predecessor, preserving the
validity of all outstanding references.

## Mailbox

Each actor has exactly one mailbox. All senders enqueue messages into
it. When the same actor sends multiple messages to the same target,
they arrive in send order. Messages from different actors have no
defined relative ordering.

The default mailbox is a FIFO queue — messages are processed in
enqueue order. A priority mailbox enqueues by message priority,
potentially placing high-priority messages at the front.

The current behavior must handle whatever message is dequeued next.
There is no scanning the mailbox for a matching message. Failure to
handle a message is treated as a failure.

## Protocol typing

Reply types are expressed by embedding a typed actor ref for the
reply-to address inside the message. The receiver sends its reply
through that ref, and the reply type is statically enforced. If the
reply itself contains another typed ref, the conversation continues
with a new message type — encoding the protocol's current state in
the type system.

## Lifecycle

Actors are not garbage-collected when unreferenced. You must ensure
each actor is eventually terminated to release its resources.

On restart, internal state is recreated from scratch — the
constructor runs again. Optionally, state can be recovered by
persisting received messages and replaying them after restart (event
sourcing).

On termination, remaining mailbox messages drain to the system's
dead letter mailbox and are forwarded to the EventStream as
DeadLetters. The actor ref's mailbox is replaced with a system
mailbox that redirects all future messages to DeadLetters. This is
best-effort — do not rely on it for guaranteed delivery.

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
