# Safety and liveness

Safety and liveness are the two correctness properties of concurrent systems.
A safety failure gives the wrong answer. A liveness failure gives no answer.

## Safety: nothing bad happens

Safety concerns data integrity. A violation occurs when the system reaches an
incorrect state—two threads receiving the same ID from a sequence generator,
or an account balance going negative due to a race condition.

Safety is achieved through mutual exclusion (locks) and atomicity. The
trade-off: more locking increases the risk of liveness failures.

## Liveness: something good eventually happens

Liveness concerns progress. A violation occurs when the program stops doing
useful work even though data remains uncorrupted.

In a single-threaded program, a liveness failure is almost always an infinite
loop. In multithreaded systems, failures arise from interactions between
threads competing for shared resources.

### Deadlock

A circular dependency on resources. Thread A holds Lock 1 and waits for
Lock 2. Thread B holds Lock 2 and waits for Lock 1. Neither can proceed.
Result: total halt of the involved threads.

### Starvation

A thread is perpetually denied the resources it needs. A low-priority thread
is repeatedly preempted by higher-priority threads and never gets scheduled.
Result: indefinite delay without a hard lock.

### Livelock

Threads are not blocked but are stuck reacting to each other without making
forward progress—like two people in a hallway, each stepping aside in the
same direction, then correcting in the same direction, endlessly. Result:
high CPU usage with zero productive output.

## The tension

Safety and liveness pull in opposite directions:

| Strategy              | Safety                          | Liveness risk                     |
|-----------------------|---------------------------------|-----------------------------------|
| Aggressive locking    | High, data stays correct        | High, deadlocks and contention    |
| Minimal locking / CAS | Lower, race conditions possible | Low, threads always make progress |

Correct concurrent programs must satisfy both properties simultaneously.

## Related

- [Thread safety hazards](thread-safety-hazards.md) - The safety side in detail

---

Return to [Concurrency](_index.md)
