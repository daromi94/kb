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

```
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

## Supervisor strategies

The parent defines a supervisor strategy when starting a child. The
strategy maps failure types to recovery actions:

| Action  | Effect                              |
|---------|-------------------------------------|
| Restart | Reinitialize child with fresh state |
| Stop    | Terminate child permanently         |

Children never die silently (except infinite loops). A failing child
triggers the supervisor strategy; a stopped child notifies interested
parties. Restarts are invisible to collaborating actors — they can keep
sending messages while the target actor restarts.

## Related

- [Call stack illusion](call-stack-illusion.md) - The failure-handling
  problem that supervision solves

---

Return to [Pekko](_index.md)
