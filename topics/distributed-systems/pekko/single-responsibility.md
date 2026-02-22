# Single responsibility

An actor should do one thing well. When an actor accumulates
unrelated state or mixes risky I/O with critical logic, it becomes
hard to supervise, test, and reason about. The fix is to push each
distinct responsibility into a separate child actor.

## Why single-purpose actors matter

Supervision is applied per actor. A multi-responsibility actor forces
one supervision strategy on all its concerns. If a database call and
a JSON parse live in the same actor, a parse failure restarts the
database connection too. Splitting them lets each child have its own
strategy — restart the parser, leave the connection alone.

Testability improves for the same reason. A small actor with one
behavior and one piece of state is straightforward to unit test.
A large actor with interleaved concerns requires elaborate setup
to exercise each code path.

## When to split

Create a child actor when:

- **State is unrelated.** The actor manages multiple maps, counters,
  or connections that serve different purposes. Each group of related
  state belongs in its own actor.
- **Error handling differs.** One concern should restart on failure
  while another should stop or resume. Different supervision
  strategies require different actors.
- **Blocking is unavoidable.** A legacy driver or synchronous API
  must block. Isolate it in a child on a dedicated dispatcher so
  the parent's mailbox stays responsive.

## Single actor vs specialized children

| Aspect      | Single actor              | Specialized children         |
|-------------|---------------------------|------------------------------|
| Fault scope | One failure kills all     | Failure affects one sub-task |
| Supervision | One strategy for all      | Per-child strategy           |
| Testability | Complex setup, many paths | Focused unit tests           |
| Throughput  | Single mailbox bottleneck | Children process in parallel |

## Related

- [Error kernel pattern](error-kernel-pattern.md) - Protecting
  state by delegating risk to children
- [Hierarchical design](hierarchical-design.md) - Broader design
  guidelines for actor hierarchies
- [Supervision](supervision.md) - Per-child fault handling
  strategies

---

Return to [Pekko](_index.md)
