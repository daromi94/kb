# Supervision

Actors handle errors through two mechanisms: domain errors become
ordinary reply messages, and internal faults are handled by a mandatory
parent-child supervision hierarchy.

## Two kinds of errors

**Domain errors** occur when a delegated task fails for expected reasons
(e.g., invalid input). The service actor itself is healthy — only the
task is erroneous. The actor replies with a message describing the
error. No special mechanism is needed; errors are part of the domain.

**Internal faults** occur when the actor itself encounters an
unexpected failure (a bug, a corrupted resource). The actor cannot
recover on its own.

## The actor tree

Pekko organizes all actors into a tree hierarchy. An actor that creates
another actor becomes its parent. This mirrors how operating systems
organize processes. When a parent stops, all its children stop
recursively.

```text
      +----------+
      |  Parent  |
      +----+-----+
           |
     +-----+------+
     |             |
+----+----+  +----+----+
| Child A |  | Child B |
+---------+  +---------+
```

Every actor has exactly one supervisor: its parent. There is always a
responsible entity for managing an actor.

The parent maintains a list of its children in its context. Spawning
or stopping a child updates this list immediately. The actual
creation and termination happen asynchronously behind the scenes —
they never block the parent.

## Supervision cycle

When an actor throws an exception during message processing:

1. The actor suspends its mailbox
2. A failure signal (containing the exception) is sent to the parent
3. The parent applies its supervisor strategy based on the failure type
4. The child is instructed to resume, restart, or stop

## Supervisor strategies

The parent defines a supervisor strategy when starting a child. The
strategy maps failure types to recovery actions:

| Action  | Effect                                        |
|---------|-----------------------------------------------|
| Resume  | Keep the child running with its current state |
| Restart | Reinitialize child with fresh state           |
| Stop    | Terminate child permanently                   |

Children never die silently (except infinite loops). A failing child
triggers the supervisor strategy; a stopped child notifies interested
parties.

## Restart mechanics

On restart, the ActorRef stays the same — other actors keep sending
messages to the same address. Behind the ref, the old behavior
instance is replaced with a fresh one created from the original
factory.

The restart sequence:

1. The old behavior receives a PreRestart signal (for resource
   cleanup such as closing connections)
2. A new behavior instance is created from the original factory
3. The new instance resumes processing the next message in the
   mailbox

The mailbox is preserved — queued messages are not lost. The message
that caused the failure is not re-processed. If it were, a
systematic bug (e.g., a malformed message triggering divide-by-zero)
would cause an infinite crash loop.

## Backoff restarts

When a restart fails immediately (e.g., a database is still down),
the actor crashes again, creating a hot loop that wastes CPU.
Backoff supervision adds exponential delay between restarts
(e.g., 1s, 2s, 4s, 8s), giving the external resource time to
recover before the actor reinitializes.

## Failure propagation

When all children of an actor stop unexpectedly, it often makes sense
for the parent itself to restart or stop to restore a functional
state. Combine supervision with death watch: the parent watches its
children for termination and reacts accordingly, bubbling permanent
failures up through the hierarchy.

## Related

- [Call stack illusion](call-stack-illusion.md) - The failure-handling
  problem that supervision solves
- [Hierarchical design](hierarchical-design.md) - Structuring actor
  hierarchies around supervision
- [Actors](actors.md) - The actor model and its primitives

---

Return to [Pekko](_index.md)
