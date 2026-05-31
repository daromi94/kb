# Thread safety

Thread safety means managing access to shared, mutable state. You can
talk about it as a property of code, but the real goal is to protect data
from uncontrolled concurrent access.

## State

An object's state is its data, held in state variables such as instance or
static fields. It encompasses any data that can affect the object's
externally visible behavior, including fields from dependent objects: a
HashMap holds part of its state in the map object and the rest across many
Map.Entry objects.

Two properties of state decide whether it needs protection:

- **Shared:** more than one thread can access the variable.
- **Mutable:** its value can change during its lifetime.

Whether an object needs to be thread-safe depends on whether multiple
threads access it, a property of how the program uses the object rather
than what the object does.

## Protecting shared state

Whenever more than one thread accesses a state variable and at least one of
them writes to it, all of them must coordinate that access through
synchronization. Skip this coordination and the program is broken, open to
data corruption, lost updates, and stale reads.

Three strategies fix unsynchronized access to shared mutable state:

- Don't share the variable across threads.
- Make the variable immutable.
- Synchronize every access to the variable.

In Java the primary synchronization mechanism is the synchronized keyword,
which provides exclusive locking. The term also covers volatile variables,
explicit locks, and atomic variables.

## Designing for thread safety

Design a class to be thread-safe from the start; retrofitting safety onto an
existing class is far harder. Encapsulation, immutability, and a clear
specification of invariants are the techniques that make the job tractable.

A thread-safe class encapsulates its own synchronization, so clients need
not add any themselves.

## Correctness

Correctness means a class conforms to its specification. A good
specification states invariants that constrain the object's state and
postconditions that describe the effects of its operations.

**Thread-safe class:** a class that behaves correctly when accessed from
multiple threads, regardless of how the runtime schedules or interleaves
those threads, and with no additional coordination on the part of the
calling code.

When such a class is correctly implemented, no sequence of public
operations—method calls, field reads, field writes—can drive an instance
into an invalid state, whether those operations run sequentially or
concurrently.

Stateless objects are always thread-safe. With no state to share, they
give concurrent threads nothing to corrupt.

---

Return to [Concurrency](_index.md)
