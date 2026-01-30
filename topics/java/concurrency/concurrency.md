# Concurrency

Concurrency is the ability of a system to handle multiple tasks by allowing them
to start, run, and complete in overlapping time periods.

Concurrency is about **dealing with** many things at once. Parallelism is about
**doing** many things at once.

## The coffee shop analogy

- **Sequential:** One cashier takes an order, makes the coffee, hands it to the
  customer, then calls the next person. If the milk takes two minutes to steam,
  the line stands still.
- **Concurrent:** One cashier takes an order, hands a ticket to the barista, and
  immediately calls the next customer. While the milk is steaming for the first
  order, the cashier processes the second. Even one person can manage multiple
  orders by switching between tasks during idle moments.
- **Parallel:** Two cashiers and two espresso machines. Two customers are served
  at the exact same physical moment.

## Interleaving and context switching

In a system with a single CPU core, true simultaneous execution is impossible.
The system achieves concurrency through **interleaving**.

The operating system scheduler gives each task a tiny slice of time (a quantum).
It rapidly switches between tasks—pausing one and resuming another—so quickly
that it creates the illusion of simultaneous progress. Saving the state of one
task and loading the state of another is called **context switching**.

## Why use concurrency

The primary goal isn't necessarily to make a single calculation faster, but to
make the system more efficient and responsive.

**Hiding latency:** Most programs spend time waiting—for a user click, a file
download, or a database query. Concurrency allows the CPU to do other work
during that dead time.

**Responsiveness:** In a web browser, concurrency lets you scroll a page while a
heavy image loads in the background. Without it, the entire application would
freeze until the download finished.

**Better throughput:** By overlapping I/O-bound tasks, a system can complete
significantly more work in the same total window of time.

## Concurrency as structure

In modern software design, concurrency is treated as a way to **structure** a
program. Breaking a monolithic process into independent, smaller tasks that
communicate with each other makes the code more modular. This concurrent
structure allows the program to scale naturally: run it on a machine with 16
cores, and the concurrent tasks can be mapped to those cores to run in parallel
without changing the underlying logic.
