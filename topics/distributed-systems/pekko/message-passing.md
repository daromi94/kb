# Message passing

Actors communicate exclusively through asynchronous messages. Sending a
message does not transfer the thread of execution to the recipient —
the sender continues immediately without blocking.

## Messages vs method calls

| Aspect    | Method call             | Message send            |
|-----------|-------------------------|-------------------------|
| Execution | Transfers to callee     | Sender continues        |
| Return    | Value returned on stack | Reply sent as a message |
| Threading | Same thread             | Independent threads     |
| Blocking  | Caller waits            | Caller never blocks     |

Messages have no return value. If an actor needs a result, the receiver
delivers it as a separate reply message. Blocking for a return would
force the sender to either stall or execute the receiver's work on its
own thread — defeating the purpose of delegation.

## Sequential processing preserves invariants

Each actor processes messages one at a time. Since at most one message
is being handled at any moment, internal state can be modified without
synchronization. Invariants hold automatically — no locks required.

Different actors run concurrently with each other, so the system
processes as many messages in parallel as hardware allows.

## Message lifecycle

1. Message arrives and is appended to the mailbox
2. If the actor is idle, it is marked ready to execute
3. The scheduler picks up the actor and assigns a thread
4. The actor dequeues the message from the front of the mailbox
5. The actor processes the message — modifying state, sending messages
6. The actor is unscheduled, freeing the thread

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

## Scheduling

Actors are lightweight — roughly 300 bytes of overhead each. Millions
of actors share a small pool of threads. The scheduler multiplexes
actors onto threads transparently, making task delegation the natural
mode of operation.

In a large system the exact order in which actors process messages is
not controllable and not intended to be. The system determines
scheduling; application logic should not depend on global ordering.

## Related

- [Actors](actors.md) - Actor model fundamentals
- [Actor lifecycle](actor-lifecycle.md) - Actor creation and termination
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - Why OOP breaks under concurrency
- [Shared memory illusion](shared-memory-illusion.md) - Hardware reality of memory
- [Call stack illusion](call-stack-illusion.md) - Hardware reality of threads

---

Return to [Pekko](_index.md)
