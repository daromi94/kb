# Actor lifecycle

Actors are not garbage-collected. Each actor must be explicitly
terminated to release its resources — either by itself, its parent,
or through supervision.

## Creation

Actors are created by calling `context.spawn(behavior, name)` from
within an existing actor, or by providing a root behavior to
`ActorSystem.create(...)`. The spawning actor becomes the parent,
establishing the supervision relationship.

## Termination

An actor stops when it returns `Behaviors.stopped`, when its parent
stops (recursive), or when its supervisor decides to stop it after
a failure.

On termination, remaining mailbox messages drain to the system's
dead letter mailbox and are forwarded to the EventStream as
DeadLetters. The actor ref's mailbox is replaced with a system
mailbox that redirects all future messages to DeadLetters. This is
best-effort — do not rely on it for guaranteed delivery.

## Related

- [Actors](actors.md) - Actor model fundamentals
- [Message passing](message-passing.md) - Mailbox mechanics
- [Supervision](supervision.md) - Restart mechanics
- [Death watch](death-watch.md) - Observing termination

---

Return to [Pekko](_index.md)
