# Thread safety

Thread safety is about managing access to shared, mutable state. The goal
is to protect data from uncontrolled concurrent access.

## State

An object's state is the data that determines its externally visible
behavior: the values in its instance and static fields, and any such data
held in dependent objects.

State needs protection only when it is both shared and mutable:

- **Shared:** more than one thread can reach it.
- **Mutable:** its value can change during its lifetime.

Whether an object needs thread safety therefore depends on how it is used,
not on what it does.

## Coordinating access

When multiple threads access the same state and at least one of them writes
to it, they must coordinate that access. Without coordination, the program
is broken, open to data corruption, lost updates, and stale reads.

Three strategies remove the risk:

- Don't share the variable across threads
- Make the variable immutable
- Synchronize every access to the variable

In Java the primary synchronization mechanism is the synchronized keyword,
which provides exclusive locking. The term also covers volatile variables,
explicit locks, and atomic variables.

## Designing for thread safety

Design a class to be thread-safe from the start; retrofitting safety onto an
existing class is far harder. Encapsulation, immutability, and a clear
specification of invariants are the techniques that make the job tractable.

A thread-safe class encapsulates its own synchronization, so clients need
not add any themselves.

## What a thread-safe class guarantees

**Thread-safe class:** a class that behaves correctly when accessed from
multiple threads, regardless of how the runtime schedules or interleaves
those threads, and with no additional coordination on the part of the
calling code.

Correctness here means conforming to a specification: the invariants that
constrain the object's state and the postconditions that describe the
effects of its operations. In a correctly implemented thread-safe class, no
sequence of public operations—method calls, field reads, field writes—can
drive an instance into an invalid state, whether those operations run
sequentially or concurrently.

Stateless objects are always thread-safe. With no state to share, they give
concurrent threads nothing to corrupt.

---

Return to [Concurrency](_index.md)
