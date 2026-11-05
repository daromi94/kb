# Is the Linux kernel preemptive?

Yes. Linux uses preemptive scheduling, and it also supports preemption of code executing inside the kernel. However, these are two different concepts, and the degree of kernel preemptibility depends on its configuration.

## 1. What is preemption?

**Preemption is the ability of the operating system to suspend a running task and give the CPU to another task without requiring the first task to voluntarily relinquish it.**

Consider a CPU executing two threads:

```text
Time ---------------------------------------->

CPU
| Thread A | Thread B | Thread A | Thread B |
           ^          ^          ^
           |          |          |
      Preemption Preemption Preemption
```

Thread A might be executing an infinite loop:

```c
while (true) {
    compute();
}
```

Without preemptive scheduling, Thread A could monopolize the CPU indefinitely because it never voluntarily yields.

With preemptive scheduling, the kernel can interrupt Thread A's execution, save its CPU state, and schedule Thread B.

This allows multiple runnable threads to share the same CPU.

### How does preemption work?

A simplified sequence:

```text
  CPU executing Thread A
             |
             v
      Timer interrupt
             |
             v
   Kernel gains control
             |
             v
 Scheduler evaluates tasks
             |
             v
   Should Thread B run?
             |
             v
            Yes
             |
             v
  Save Thread A CPU state
             |
             v
Restore Thread B CPU state
             |
             v
   CPU executes Thread B
```

The actual scheduler decision depends on scheduling policies, priorities, task eligibility, and CPU scheduling history.

A timer interrupt is one possible trigger, but preemption can also occur when another task becomes runnable—for example, when an I/O operation completes.

## 2. User-space preemption vs. kernel preemption

This distinction is particularly important.

### User-space preemption

A thread executing application code can be preempted by the kernel.

```text
        CPU
         |
         v
User-space Thread A
         |
         |  Timer interrupt
         v
 Kernel scheduler
         |
         |  Context switch
         v
User-space Thread B
```

The application does not need to cooperate.

This behavior is fundamental to modern Linux scheduling.

### Kernel preemption

Now consider a thread executing a system call:

```c
read(fd, buffer, size);
```

The CPU transitions from user mode into kernel mode.

```text
      Thread A
          |
          v
   User-space code
          |
          | read()
          v
  Kernel-space code
          |
          | Processing syscall
          |
          v
Return to user space
```

**Kernel preemption means that Thread A can be suspended while it is still executing kernel code, allowing another task to run.**

For example, on a fully preemptible kernel:

```text
      Thread A
          |
          v
   User-space code
          |
          | read()
          v
  Kernel-space code
          |
          | Thread B needs CPU
          v
     Preemption
          |
          v
  Thread B executes
          |
          | Thread A scheduled again
          v
  Kernel-space code
          |
          | Continue read()
          v
Return to user space
```

Notice that Thread A does not have to finish its system call before Thread B can execute.

That is the central advantage of preemptible kernel execution.

## 3. Is all Linux kernel code preemptible?

No.

Linux supports several preemption models.

| Model               | Behavior                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| `PREEMPT_NONE`      | Kernel preemption only at explicit rescheduling points, blocking operations, or return to user mode. |
| `PREEMPT_VOLUNTARY` | Adds more explicit opportunities to reschedule within the kernel.                                    |
| `PREEMPT_LAZY`      | Allows scheduler-controlled delayed preemption for ordinary tasks.                                   |
| `PREEMPT` (Full)    | Allows kernel code to be preempted wherever preemption is enabled.                                   |
| `PREEMPT_RT`        | Makes much more kernel execution preemptible, including much interrupt processing.                   |

**Even on a fully preemptible Linux kernel, certain critical sections cannot be preempted.**

For example:

```c
preempt_disable();

/* Critical section */

preempt_enable();
```

Between `preempt_disable()` and `preempt_enable()`, the currently executing task cannot be involuntarily scheduled out on that CPU.

This is important for protecting certain kernel operations and per-CPU data structures.

On ordinary non-RT kernels, acquiring a `spinlock_t` also disables preemption. `PREEMPT_RT` changes that behavior for regular spinlocks but retains non-preemptible regions using mechanisms such as `raw_spinlock_t`.

## 4. Why doesn't Linux make everything preemptible?

Because preemption introduces trade-offs.

Advantages:

- Lower scheduling latency for tasks that need CPU time.
- Better responsiveness under CPU contention.
- Reduced risk that long-running kernel operations delay important tasks.

Costs:

- More opportunities for context switches.
- Additional synchronization requirements.
- Potential cache disruption and scheduling overhead.
- More complex concurrency behavior inside the kernel.

A particularly important distinction is that **preemption improves the ability to schedule tasks promptly; it does not automatically improve throughput.**

For example, a high-throughput networking application may prefer fewer context switches and more uninterrupted CPU execution, while a real-time control application may prioritize bounded scheduling latency.

## 5. Preemption is not the same as an interrupt

**An interrupt transfers execution to a handler, which may run independently of the normal task scheduler.**

**Preemption changes which task is executing.**

A hardware interrupt can cause the scheduler to make a preemption decision, but an interrupt does not necessarily result in a task switch.

Similarly, **disabling task preemption does not automatically disable hardware interrupts.**

These are separate mechanisms.

In summary: Linux uses a preemptive scheduler, meaning running tasks do not have exclusive ownership of the CPU. Kernel preemption extends this capability to execution inside the kernel itself, subject to configuration and critical-section restrictions.
