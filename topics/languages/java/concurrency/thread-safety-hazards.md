# Thread safety hazards

The JVM and underlying hardware prioritize performance over intuitive
execution order. Without explicit synchronization, operations from different
threads can interleave in ways that violate program correctness.

## Non-atomic operations

A seemingly atomic Java expression like `value++` compiles into three
distinct machine-level steps:

1. **Read** the current value from memory
2. **Modify** the value (increment by 1)
3. **Write** the updated value back to memory

The thread scheduler can suspend a thread between any of these steps,
allowing another thread to intervene mid-operation.

## Race conditions

A race condition occurs when correctness depends on the relative timing of
multiple threads. The classic example is **read-modify-write** on shared
state:

```
Thread A: read value  (sees 9)
Thread B: read value  (sees 9)
Thread A: write value (stores 10)
Thread B: write value (stores 10)  <- Thread A's update is lost
```

Two increments produced a net change of one. Thread B's read occurred before
Thread A's write was committed, so Thread A's update was silently
overwritten.

## Reordering

To optimize execution, the compiler and CPU may reorder instructions as long
as the result in a single-threaded context remains the same. In a
multithreaded context, these reorderings can cause a thread to observe a
partially constructed object or inconsistent state that would be impossible
under sequential execution.

## Memory visibility

CPUs use hierarchical caches (L1, L2, L3). A thread may update a value in
its local cache without immediately flushing to main memory. Other threads
on different cores continue reading the stale value from their own caches.
Without synchronization, there is no guarantee that a write by one thread
will ever become visible to another.

## Three requirements for safety

| Requirement | Guarantee                                     | Failure mode                              |
|-------------|-----------------------------------------------|-------------------------------------------|
| Atomicity   | Operations complete as an indivisible unit    | Lost updates (two increments yield +1)    |
| Visibility  | Writes by one thread are seen by all others   | Threads read stale data                   |
| Ordering    | Instructions execute in the expected sequence | Observing inconsistent intermediate state |

**`synchronized`** provides all three: mutual exclusion (atomicity), memory
fencing (visibility), and a happens-before edge (ordering).

**`AtomicInteger`** and related classes use hardware Compare-and-Swap (CAS)
instructions to achieve atomicity and visibility without locking, at the cost
of requiring retry loops under contention.

## Related

- [Thread memory](thread-memory.md) - Shared vs. thread-private state
- [Threads](threads.md) - Thread fundamentals and creation

---

Return to [Concurrency](_index.md)
