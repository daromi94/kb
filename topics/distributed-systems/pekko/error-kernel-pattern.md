# Error kernel pattern

The error kernel pattern organizes actors into layers based on how
critical their state is. Important state lives in high-level actors
kept deliberately simple. Dangerous operations — I/O, parsing,
network calls — are pushed down to disposable child actors whose
crashes cannot destroy the parent's state.

## Push risk down

Code that does heavy lifting (calling APIs, querying databases,
parsing untrusted input) is the code most likely to fail. If the
actor holding critical state performs that work directly, a single
failure destroys both the work and the state.

The pattern separates these concerns:

- **Kernel actors** hold the source of truth. They stay simple,
  delegate risky work, and supervise the outcome.
- **Worker actors** perform one dangerous task each. If they crash,
  only their local, ephemeral state is lost.

## Layered hierarchy

```text
+---------------------------------+
|  Guardian (thin, boots system)  |
+---------+-----------------------+
          |
+---------+-----------------------+
|  Manager / Kernel               |
|  Holds long-lived state         |
|  Delegates I/O to children      |
+---------+----------+------------+
          |          |
     +----+----+ +---+-----+
     | Worker  | | Worker  |
     | (risky) | | (risky) |
     +---------+ +---------+
```

| Layer    | Role                                             |
|----------|--------------------------------------------------|
| Guardian | Boots the system, supervises managers            |
| Kernel   | Holds state, delegates work, decides on failures |
| Worker   | Performs one risky task, disposable              |

## Failure scenario

1. A TransactionManager (kernel) receives a request and updates its
   internal pending list
2. It spawns a DatabaseWorker to persist the transaction
3. The DatabaseWorker crashes because the network is unstable
4. The TransactionManager is notified via supervision
5. The pending list is safe — the manager can retry with a new
   worker or try a different database node

Had the manager performed the database call itself and crashed,
the pending list would have been lost.

## Benefits

**Failure isolation.** A crash in a leaf actor does not propagate to
the critical state held in the parent.

**Granular supervision.** Different workers can have different restart
strategies — exponential backoff for flaky I/O, stop for
unrecoverable parse errors.

**Responsiveness.** The kernel stays alive and can serve other
requests or degrade gracefully while workers recover.

## Disposable workers

Workers are typically ephemeral, spawned per-request:

1. The kernel spawns a worker for a single task
2. It watches the worker with death watch
3. The worker sends the result back and stops, or crashes and sends
   a Terminated signal
4. The kernel handles the result or failure and moves on

This per-request lifecycle simplifies state management — each
worker's lifecycle maps to exactly one operation.

## Related

- [Hierarchical design](hierarchical-design.md) - Design guidelines
  including the error kernel principle
- [Supervision](supervision.md) - The mechanism that makes the
  pattern work
- [Death watch](death-watch.md) - Cross-hierarchy termination
  monitoring for disposable workers

---

Return to [Pekko](_index.md)
