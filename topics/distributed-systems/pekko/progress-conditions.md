# Progress conditions

Non-blocking guarantees form a hierarchy of strength. Each level
implies the ones below: wait-free > lock-free > obstruction-free.

| Guarantee           | Deadlock-free | Starvation-free | Definition                                |
|---------------------|---------------|-----------------|-------------------------------------------|
| Wait-freedom        | Yes           | Yes             | Every call finishes in finite steps       |
| Lock-freedom        | Yes           | No              | Some call always finishes in finite steps |
| Obstruction-freedom | Yes           | No              | Isolated call finishes in bounded steps   |

## Wait-freedom

A method is wait-free if every call finishes in a finite number of
steps. **Bounded wait-free** adds a finite upper bound on that step
count. Wait-free methods never block, so deadlock is impossible and
every participant progresses — no starvation.

## Lock-freedom

Infinitely often, some method call finishes in a finite number of
steps. This prevents deadlock but not starvation — individual
participants may be delayed indefinitely as long as the system as a
whole keeps making progress.

## Obstruction-freedom

A method is obstruction-free if a call that eventually runs in
isolation (no other threads take steps) finishes in bounded steps.
This is the weakest non-blocking guarantee.

Optimistic concurrency control (OCC) typically provides
obstruction-freedom. Each participant attempts its operation on the
shared object, rolls back on conflict, and retries on a schedule. If
a participant eventually runs uncontested, it succeeds.

## Related

- [Concurrency terminology](concurrency-terminology.md) -
  Blocking, deadlock, starvation definitions

---

Return to [Pekko](_index.md)
