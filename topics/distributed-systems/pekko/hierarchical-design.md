# Hierarchical design

Actors naturally form hierarchies by splitting tasks into smaller,
manageable pieces delegated to child actors. Each resulting actor has a
clear role: which messages it handles, how it reacts, and how its
failures are managed.

## Why hierarchies beat defensive programming

Layered software tends toward defensive programming — catching and
suppressing every failure to prevent it from leaking out. Actor
hierarchies take the opposite approach: failures propagate to the actor
best positioned to handle them. Communicating problems to the right
place produces better solutions than sweeping them under the carpet.

## Design guidelines

**Error Kernel Pattern.** An actor with important state should never
risk that state by performing dangerous work directly. Instead, it
delegates risky sub-tasks to disposable child actors and handles their
failures through supervision. Creating a new child per request simplifies
state management for collecting replies, since each child's lifecycle
maps to exactly one request.

**Death watch.** When an actor depends on another actor to carry out its
duty, it should watch that actor's liveness and react to termination
notices. This applies across the hierarchy — not just parent-to-child.

**Single responsibility via children.** When an actor accumulates
multiple responsibilities, push each one into a separate child. This
keeps each actor's logic and state simple and independently
supervisable.

**Thin guardian.** The top-level actor is the innermost part of the
error kernel. It should only start the application's subsystems and
contain minimal logic. Overloading it strains a single point of
contention and coarsens fault handling.

## Related

- [Single responsibility](single-responsibility.md) - When and why
  to split into children
- [Error kernel pattern](error-kernel-pattern.md) - Protecting state
  by delegating risk
- [Supervision](supervision.md) - The mechanism that makes hierarchies
  fault-tolerant
- [Actors](actors.md) - Actor model fundamentals and the
  organizational mental model

---

Return to [Pekko](_index.md)
