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

## Actor anatomy

Every actor consists of five components:

| Component             | Role                                         |
|-----------------------|----------------------------------------------|
| Mailbox               | Queue where incoming messages accumulate     |
| Behavior              | Current state and message-handling logic     |
| Messages              | Data signals, analogous to method parameters |
| Execution environment | Thread pool that drives actor scheduling     |
| Address               | Identity used by other actors to send to it  |

## Message lifecycle

1. Message arrives and is appended to the mailbox
2. If the actor is idle, it is marked ready to execute
3. The scheduler picks up the actor and assigns a thread
4. The actor dequeues the message from the front of the mailbox
5. The actor processes the message — modifying state, sending messages
6. The actor is unscheduled, freeing the thread

Millions of actors can share a small pool of threads. The scheduler
multiplexes actors onto threads transparently, making task delegation
the natural mode of operation.

## Related

- [Overview](overview.md) - High-level summary of the actor model
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) -
  Why encapsulation breaks without actors
- [Shared memory illusion](shared-memory-illusion.md) - Why local
  state with message passing matches hardware
- [Call stack illusion](call-stack-illusion.md) - Why method-call
  error handling fails across threads

---

Return to [Pekko](_index.md)
