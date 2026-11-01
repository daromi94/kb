# Unit of work

A unit of work is a discrete piece of computation that a system treats as a single entity for execution, scheduling, tracking, or completion.

The important distinction is that a unit of work describes what needs to be done, not necessarily which thread or CPU executes it.

In operating systems, the meaning depends on the abstraction being discussed:

- CPU instruction: A small operation executed by the processor.
- Task or thread: An independently schedulable execution context.
- Work item: A piece of computation submitted for execution, often by a worker thread.
- I/O operation: A request for the system to perform an input/output activity.

A unit of work does not necessarily have its own thread, stack, or scheduling priority.

## 1. Work versus execution resources

Consider a system processing incoming requests.

```text
         Incoming requests
                 |
                 v
   +-------------+-------------+
   |             |             |
   v             v             v
Work A        Work B        Work C
   |             |             |
   +-------------+-------------+
                 |
                 v
            Work queue
                 |
          +------+------+
          |             |
          v             v
      Thread 1      Thread 2
          |             |
          v             v
        CPU 0         CPU 1
```

There are three distinct concepts:

1. Work: The operations that must be performed.
2. Execution contexts: The threads that execute those operations.
3. Execution resources: The CPU cores on which those threads run.

A thread can execute thousands of units of work during its lifetime. Conversely, a single logical unit of work might involve multiple threads or execution stages.

This separation is fundamental to thread pools, asynchronous execution, kernel workqueues, and task schedulers.

## 2. The unit of work in Linux scheduling

In Linux, the primary schedulable unit is a task, represented by a `task_struct`.

A Linux task generally corresponds to a thread of execution. It has execution state, scheduling attributes, and CPU context.

The kernel scheduler operates on runnable tasks, not on arbitrary functions or application-level jobs.

```text
          Linux Scheduler
                 |
                 v
          Runnable tasks
                 |
   +-------------+-------------+
   |             |             |
   v             v             v
Task A        Task B        Task C
   |             |
   v             v
 CPU 0         CPU 1
```

The scheduler decides which runnable task should execute on each available CPU.

This has an important consequence: preemption occurs at the task execution level, not necessarily at the logical unit-of-work boundary.

A thread executing Work A might be preempted halfway through it. When the thread resumes, execution continues from its saved CPU context.

## 3. Units of work in Linux kernel workqueues

Linux also has an explicit abstraction called a work item, represented by `struct work_struct`.

A kernel subsystem can submit a work item to be executed asynchronously.

For example, a device driver might submit work to perform deferred processing.

```text
            Device driver
                  |
                  | Submit work
                  v
              Workqueue
                  |
    +-------------+-------------+
    |             |             |
    v             v             v
 Work A        Work B        Work C
    |             |
    v             v
kworker 1     kworker 2
    |             |
    v             v
  CPU 0         CPU 1
```

Here:

- The work item identifies the function to execute.
- The workqueue provides the abstraction for submitting and managing deferred work.
- The worker provides the execution context.
- The scheduler schedules the worker thread on a CPU.

## 4. Why does the size of a unit of work matter?

Suppose a worker processes 1,000 requests.

There are two possibilities:

- **Fine-grained work:** Each request becomes an independent unit of work.
- **Coarse-grained work:** A batch of 100 requests becomes one unit of work.

The choice influences scheduling overhead, load balancing, responsiveness, and cache locality.

| Fine-grained work                     | Coarse-grained work                    |
| ------------------------------------- | -------------------------------------- |
| More scheduling or queueing overhead  | Less overhead per operation            |
| More opportunities for load balancing | Fewer opportunities for load balancing |
| Smaller execution batches             | Larger execution batches               |
| Potentially better responsiveness     | Potentially better cache locality      |

Importantly, a large unit of work does not necessarily monopolize a CPU: a preemptive kernel can still preempt its executing thread.

However, a cooperative runtime that only switches work at explicit boundaries may suffer from long-running units of work.

## 5. The central distinction

A useful way to understand operating systems is to separate three layers:

| Abstraction         | Central question                                      |
| ------------------- | ----------------------------------------------------- |
| Unit of work        | What computation needs to happen?                     |
| Scheduling unit     | What execution context can be scheduled or preempted? |
| Processing resource | Where does the computation execute?                   |

In Linux, these commonly correspond to work items, threads, and CPUs, respectively.

They are related but not interchangeable.

Key insight: A unit of work is a logical abstraction. A thread is an execution abstraction. A CPU is a physical execution resource. Keeping these concepts separate is essential for understanding preemption, scheduling, concurrency, and throughput.
