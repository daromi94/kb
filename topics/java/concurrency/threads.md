# Threads

A thread is the smallest unit of execution within a program—a path of execution
that allows a program to perform multiple tasks simultaneously or in an
interleaved fashion.

Every Java application starts with at least one thread, the **main thread**,
which executes the `main()` method. From there, you can spawn additional threads
to handle background tasks without freezing the user interface.

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
| ----------------- | ------------------------- | --------------------------------- |
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
