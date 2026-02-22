# Concurrency terminology

Working definitions for core concurrency concepts used throughout
Pekko's programming model.

## Concurrency vs parallelism

**Concurrency** means two or more tasks make progress, even if they do
not execute simultaneously. Time slicing across a single core is
concurrent but not parallel.

**Parallelism** means execution is truly simultaneous — multiple cores
running tasks at the same time.

## Synchronous vs asynchronous

A **synchronous** call blocks the caller until it returns a value or
throws an exception. The caller cannot make progress in the meantime.

An **asynchronous** call lets the caller continue after a finite number
of steps. Completion is signaled separately — via a callback, a Future,
or a message. Actors are asynchronous by nature: sending a message does
not wait for delivery.

A synchronous API does not necessarily block a thread — a CPU-intensive
computation behaves similarly. Asynchronous APIs are preferred because
they guarantee overall system progress.

## Blocking vs non-blocking

**Blocking** means one thread's delay can indefinitely delay others.
A thread holding a mutex indefinitely (e.g., an accidental infinite
loop) prevents all waiters from progressing.

**Non-blocking** means no thread can indefinitely delay another.
Non-blocking operations are preferred because system-wide progress is
not guaranteed in the presence of blocking.

## Deadlock, starvation, and livelock

| Condition  | Progress          | Behavior                              |
|------------|-------------------|---------------------------------------|
| Deadlock   | None              | All participants wait on each other   |
| Starvation | Partial           | Some participants never get scheduled |
| Livelock   | None (but active) | Participants keep changing state      |

**Deadlock** requires blocking — each participant waits for another to
reach a state it will never reach.

**Starvation** occurs when a scheduling policy systematically favors
some participants. A priority scheduler that always picks high-priority
tasks can starve low-priority ones indefinitely.

**Livelock** resembles deadlock in that no participant progresses, but
participants are not frozen — they continuously react to each other.
Two threads repeatedly yielding a resource to each other without either
acquiring it is a classic example.

## Race condition

A system's behavior depends on the sequence or timing of uncontrollable
events. Race conditions commonly involve shared mutable state and
interleaved thread operations, but shared state is not required. A
client sending UDP packets P1 then P2 may see the server receive P2
first — if the packets carry no ordering information, the server cannot
detect the reordering. A race condition becomes a bug only when one or
more of the possible orderings produces an undesirable outcome.

## Related

- [Progress conditions](progress-conditions.md) -
  Wait-free, lock-free, obstruction-free guarantees
- [Encapsulation and concurrency](encapsulation-and-concurrency.md) -
  How concurrency breaks OOP invariants
- [Message passing](message-passing.md) - The asynchronous,
  non-blocking communication model actors use

---

Return to [Pekko](_index.md)
