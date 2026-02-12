# Threads

A thread is a stream of program control flow within a process. Multiple threads
coexist inside the same process, sharing process-wide resources such as memory
and file handles, while each thread maintains its own program counter, stack,
and local variables.

Threads are sometimes called lightweight processes. Most modern operating
systems treat threads, not processes, as the basic units of scheduling. Without
explicit coordination, threads execute simultaneously and asynchronously with
respect to one another.

Every Java application starts with at least one thread, the **main thread**,
which executes the `main()` method. From there, you can spawn additional threads
to handle background tasks without freezing the user interface.

## Shared memory

Since threads share the memory address space of their owning process, all
threads within a process access the same variables and allocate objects from the
same heap. This allows finer-grained data sharing than inter-process mechanisms,
but without explicit synchronization a thread may modify variables that another
thread is in the middle of using, with unpredictable results.

## Platform threads

Java traditionally uses platform threads, which are thin wrappers around
operating system threads.

- **1:1 mapping:** For every `java.lang.Thread` you create, the JVM typically
  requests one thread from the underlying OS
- **Resources:** Each platform thread carries a private stack (usually 1MB) to
  store local variables and call history
- **Scheduling:** The OS scheduler decides when each thread runs on the CPU

## Virtual threads

As of Java 21, virtual threads (Project Loom) are managed by the JVM rather than
the OS. They are extremely lightweight, allowing millions of threads on a single
machine—ideal for high-throughput I/O tasks.

| Feature           | Platform threads          | Virtual threads                   |
|-------------------|---------------------------|-----------------------------------|
| **Creation cost** | Expensive (high memory)   | Cheap (low memory)                |
| **Scaling**       | Limited by OS (thousands) | Scalable to millions              |
| **Best use case** | CPU-intensive tasks       | I/O-intensive tasks (web servers) |
| **Creation**      | `new Thread(runnable)`    | `Thread.ofVirtual().start(r)`     |

## Thread lifecycle

1. **NEW:** Thread object created, `start()` not yet called
2. **RUNNABLE:** Ready to run, waiting for CPU time from the scheduler
3. **BLOCKED:** Waiting to acquire a monitor lock (entering `synchronized`)
4. **WAITING / TIMED_WAITING:** Waiting for another thread to perform an action
5. **TERMINATED:** Finished executing or stopped due to an exception

## Creating threads

### Implementing Runnable (preferred)

Separates the task from the thread itself, following composition over
inheritance.

```java
Runnable task = () -> {
    System.out.println("Running in: " + Thread.currentThread().getName());
};

Thread thread = new Thread(task);
thread.start(); // Moves from NEW to RUNNABLE
```

### Extending Thread

Less flexible because Java does not support multiple inheritance.

```java
class MyWorker extends Thread {
    public void run() {
        System.out.println("Worker thread is active.");
    }
}

MyWorker worker = new MyWorker();
worker.start();
```

## Related

- [Daemon threads](daemon-threads.md) - Background service threads
- [Executor service](executor-service.md) - Managing thread pools instead of raw threads

---

Return to [Concurrency](_index.md)
