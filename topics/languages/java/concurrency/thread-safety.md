# Thread safety

Thread safety is about managing access to shared, mutable state. The goal
is to protect data from uncontrolled concurrent access.

## State

An object's state is the data that determines its externally visible
behavior: the values in its instance and static fields, and any such data
held in dependent objects.

State needs protection only when it is both shared and mutable:

- **Shared:** more than one thread can reach it
- **Mutable:** its value can change during its lifetime

Whether an object needs thread safety depends on how it is used, not on
what it does.

## Coordinating access

When multiple threads access the same state and at least one of them writes
to it, they must coordinate access. Without coordination, the program is
broken, open to data corruption, lost updates, and stale reads.

Three strategies remove the risk:

- Don't share the state across threads
- Make the state immutable
- Synchronize every access to the state

Java's primary synchronization mechanism, the synchronized keyword, provides
mutual exclusion. Synchronization also includes volatile variables, explicit
locks, and atomic variables.

## What a thread-safe class guarantees

**Thread-safe class:** a class that behaves correctly when accessed from
multiple threads—regardless of how the runtime schedules or interleaves
them—and requires no extra coordination from callers.

Correctness means conforming to a specification: the invariants that
constrain the object's state and the postconditions that describe the
effects of its operations. In a correct thread-safe class, no sequence of
public operations—method calls, field reads, field writes—can violate its
specification, whether those operations run sequentially or concurrently.

Stateless objects are always thread-safe. With no state to share, they give
concurrent threads nothing to corrupt.

## Designing for thread safety

Design a class to be thread-safe from the start; retrofitting safety onto an
existing class is far harder. Encapsulation, immutability, and clearly
specified invariants make this tractable.

A thread-safe class encapsulates the synchronization it needs, so callers
never have to add their own.

---

Return to [Concurrency](_index.md)
