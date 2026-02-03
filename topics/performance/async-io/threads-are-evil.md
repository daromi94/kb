# Threads are evil

A famous saying in computer science (popularized by Edward A. Lee) highlighting
how difficult and dangerous multithreading can be. Threads break a fundamental
rule of programming: **determinism**. A program that works perfectly a thousand
times might crash on the thousand-and-first because of a tiny timing
difference.

## The problem of shared memory

The root of all "evil" in threading is that threads share the same memory
space. In a single-threaded or multi-process program, you know exactly what
your variables are doing. In multithreading, any thread can change any piece of
data at any time.

### Race condition example

Two threads trying to increment a counter `count = count + 1`:

1. Thread A reads the value (10)
2. Thread B reads the same value (10)
3. Thread A adds 1 and writes back (11)
4. Thread B adds 1 and writes back (11)

Even though two operations happened, the count only went up by one.

## The deadly embrace (deadlock)

To fix race conditions, we use locks (mutexes). But locks introduce deadlocks.

A deadlock happens when:

- Thread A holds Lock 1 and waits for Lock 2
- Thread B holds Lock 2 and waits for Lock 1

Neither can move, and the application freezes. Finding these bugs in large
codebases is notoriously difficult.

## Heisenbugs

Threads create bugs that are almost impossible to reproduce or debug, called
**Heisenbugs**:

- Adding a print statement to debug changes the program's timing
- The tiny delay might cause the bug to disappear while you're looking at it
- The bug reappears once you remove the debug code

## Performance lies

Many developers use threads for speed, but threads often make things slower:

**Context switching:** The OS spends more time swapping threads in and out of
the CPU than actually running code.

**Lock contention:** If many threads wait for the same lock, they sit idle,
wasting resources.

## Better alternatives

Modern technologies avoid threads for application logic:

| Technology    | Approach                                                        |
|---------------|-----------------------------------------------------------------|
| Node.js       | Async I/O (single-threaded) avoids locks and race conditions    |
| Go / Erlang   | Message passing between actors/goroutines instead of shared     |
|               | memory                                                          |
| Multi-process | Each task gets its own memory; one crash won't take down others |

## Related

- [Multithreading](multithreading.md) - The model this critique addresses
- [Asynchronous I/O](asynchronous-io.md) - A safer alternative for I/O tasks
