# PREEMPT_RT-configured Linux Kernel

PREEMPT_RT is a Linux kernel configuration that makes almost all kernel execution preemptible, with the primary goal of minimizing worst-case scheduling latency.

In other words, it transforms Linux into a real-time operating system by allowing high-priority tasks to interrupt most ongoing kernel operations, rather than waiting for those operations to finish.

The objective is not necessarily to make execution faster. It is to make the time required to respond to important events more predictable.

PREEMPT_RT achieves this primarily through two mechanisms:

1. Replacing many traditional spinning locks with preemptible locks that support priority inheritance.
2. Moving most interrupt handling into schedulable kernel threads.

These changes make most kernel execution subject to the scheduler.

## 1. Why is PREEMPT_RT necessary?

Consider a system running two tasks:

- Task A: A low-priority thread executing a system call.
- Task B: A high-priority real-time thread that needs to execute immediately.

Suppose Task A is executing a kernel operation that cannot be preempted.

```text
Time -------------------------------------------------->

CPU:

     Task A executing kernel code
     *-----------------------------*
                                   |
                                   v
                              Task B runs

               ^
               |
         Task B becomes
           runnable

     Task B must wait until the kernel
     reaches a safe preemption point.
```

Even though Task B has higher priority, it cannot execute immediately.

The reason is that the kernel might be executing a critical section with preemption disabled.

Now consider a PREEMPT_RT kernel.

```text
Time -------------------------------------------------->

CPU:

     Task A        Task B         Task A
     *--------*----------------*----------*
              ^
              |
         Task B becomes
           runnable

     Task B preempts Task A, even though
     Task A was executing kernel code.
```

This is possible when Task A is executing preemptible kernel code and Task B has a sufficiently high scheduling priority.

PREEMPT_RT reduces the amount of time that a high-priority task can be prevented from executing by lower-priority kernel activity.

## 2. What does real-time actually mean?

A real-time operating system is designed around timing constraints, not simply execution speed.

Consider a control system that must respond to an event within 100 microseconds.

Two systems might exhibit the following hypothetical scheduling latencies:

| Metric           | Standard Linux | PREEMPT_RT Linux |
| ---------------- | -------------- | ---------------- |
| Average          | 5 us           | 8 us             |
| 99th percentile  | 30 us          | 15 us            |
| Maximum observed | 500 us         | 40 us            |

Illustrative values only, not benchmark measurements.

Standard Linux has better average latency in this example, but sometimes takes 500 microseconds to respond.

PREEMPT_RT has slightly higher average latency, but its worst observed response is substantially lower.

For real-time workloads, the second behavior may be preferable.

The relevant quantity is often scheduling latency:

```text
L_sched = t_running - t_runnable
```

This measures the delay between a task becoming runnable and actually starting or resuming execution.

Importantly, PREEMPT_RT does not automatically guarantee a particular maximum latency. Hardware, drivers, firmware, system configuration, and workload interference still matter.

## 3. How does PREEMPT_RT work internally?

### A. It changes the behavior of spinlocks

In a conventional Linux kernel, acquiring a `spinlock_t` normally disables preemption.

Consider:

```c
spin_lock(&lock);

/* Critical section */

spin_unlock(&lock);
```

While holding the lock, the current thread cannot be preempted by the scheduler.

This prevents certain forms of concurrency problems, but it also introduces scheduling latency.

```text
Standard Linux

Low-priority Task A
       |
       v
Acquire lock
       |
       v
Preemption disabled
       |
       |  High-priority Task B
       |  becomes runnable
       |
       v
Release lock
       |
       v
Preemption enabled
       |
       v
Task B executes
```

With PREEMPT_RT, regular `spinlock_t` locks are implemented using an RT-mutex-based mechanism.

Instead of making the entire critical section non-preemptible, the lock allows preemption.

If acquiring the lock would require waiting, the thread can sleep rather than indefinitely spinning.

This makes the execution of critical sections more compatible with real-time scheduling.

However, some low-level kernel operations still require traditional non-preemptible spinlocks, represented by `raw_spinlock_t`.

### B. It introduces priority inheritance

Consider three threads:

| Thread | Priority | State              |
| ------ | -------- | ------------------ |
| A      | High     | Waiting for a lock |
| B      | Medium   | Runnable           |
| C      | Low      | Holding the lock   |

Thread C holds a lock that Thread A needs.

However, Thread B has higher priority than C and can prevent C from running.

```text
Task A (High priority)
       |
       | Waiting for lock
       v
     Lock X
       ^
       | Owned by
       |
Task C (Low priority)
       ^
       |
Cannot run because
       |
Task B (Medium priority)
```

This is called priority inversion.

The highest-priority task is indirectly blocked by a medium-priority task that does not even use the contested lock.

PREEMPT_RT addresses this through priority inheritance.

When Task A blocks on the lock, Task C temporarily inherits Task A's priority.

```text
Task A (High)
       |
       | Waiting
       v
     Lock X
       ^
       |
Task C (Boosted to High)
       |
       | Runs and releases lock
       v
Task A can continue
```

This prevents medium-priority tasks from indefinitely delaying the lock owner merely because of its original low priority.

The mechanism is implemented through the kernel's `rtmutex` infrastructure.

### C. It moves interrupt handling into threads

This is another major architectural change.

In a conventional Linux kernel, a hardware interrupt can cause the CPU to execute an interrupt handler directly.

```text
Hardware interrupt
       |
       v
CPU enters
IRQ context
       |
       v
IRQ handler
       |
       v
Return to task
```

Interrupt handlers execute outside normal task scheduling, and significant work performed in hard interrupt context cannot be preempted by an ordinary runnable task.

PREEMPT_RT changes this by moving most interrupt processing into kernel threads.

```text
Hardware interrupt
         |
         v
Minimal IRQ handler
         |
         | Wake thread
         v
    IRQ thread
         |
         v
  Linux scheduler
         |
    +----+----+
    |         |
    v         v
IRQ work   Higher-priority
           real-time task
```

The IRQ thread becomes schedulable, meaning that:

- Its execution can be preempted.
- It has an explicit scheduling priority.
- Higher-priority tasks can interrupt its execution.
- The scheduler can manage its CPU usage.

By default, threaded interrupt handlers use `SCHED_FIFO` with priority 50, although priorities can be changed.

Some interrupts must remain in hard interrupt context, particularly low-level operations required for scheduling and hardware management.

## 4. What remains non-preemptible?

PREEMPT_RT does not make every instruction in the kernel preemptible.

Some operations must remain atomic or execute without interruption.

Examples include:

- Low-level interrupt entry and handling.
- Parts of the scheduler itself.
- Critical sections protected by `raw_spinlock_t`.
- Explicitly preemption-disabled regions.
- Certain architecture-specific operations.

A useful conceptual model:

```text
             Linux kernel
                  |
      +-----------+-----------+
      |                       |
      v                       v
Preemptible code       Non-preemptible code
      |                       |
 Most kernel work       Low-level critical
 Threaded interrupts    sections
 Regular spinlocks      Raw spinlocks
 Deferred processing    Scheduler internals
```

The objective of PREEMPT_RT is to minimize the duration and frequency of non-preemptible execution, not eliminate it entirely.

## 5. Does PREEMPT_RT improve performance?

It depends on how performance is defined.

| Property                      | Typical effect of PREEMPT_RT |
| ----------------------------- | ---------------------------- |
| Worst-case scheduling latency | Significantly improved       |
| Scheduling predictability     | Improved                     |
| Average execution latency     | Can improve or worsen        |
| Maximum throughput            | May decrease                 |
| Context-switch overhead       | May increase                 |
| Synchronization overhead      | May increase                 |
| Real-time responsiveness      | Improved                     |

Consider a high-throughput packet-processing application.

On a conventional kernel, the application may benefit from batching, long execution periods, and minimal context switching.

PREEMPT_RT can introduce additional synchronization and scheduling overhead.

Consequently, workloads optimized for maximum throughput may not benefit from PREEMPT_RT unless they also have strict scheduling-latency requirements.

On the other hand, industrial automation, robotics, audio processing, and time-sensitive control systems frequently benefit from predictable scheduling.

## 6. The fundamental architectural insight

A conventional Linux kernel prioritizes a balance between general-purpose throughput, fairness, responsiveness, and overhead.

PREEMPT_RT changes this balance by placing significantly more kernel execution under scheduler control.

```text
Conventional Linux

Kernel execution
       |
       v
Some operations run
without preemption
       |
       v
High-priority tasks
can be delayed

PREEMPT_RT

Kernel execution
       |
       v
Most operations are
preemptible and schedulable
       |
       v
High-priority tasks
can execute sooner
```

The central idea is that even kernel work should generally not be allowed to delay a more important real-time task unnecessarily.

This is why PREEMPT_RT is fundamentally about reducing scheduling latency and improving timing predictability, rather than making Linux universally faster.
