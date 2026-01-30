# Daemon threads

A daemon thread is a low-priority thread that runs in the background to provide
services to user threads (normal threads that perform application logic).

The defining characteristic: **the JVM terminates once all user threads finish,
even if daemon threads are still running.**

## The service provider role

Daemon threads exist only to support the primary work of the application.

- **Garbage collection:** The JVM runs the GC as a daemon thread to clean up
  memory while your code executes
- **Finalizer:** Another internal JVM thread that performs cleanup for objects
  before removal from memory
- **Monitoring/housekeeping:** Auto-saving documents, background spell-checking,
  or cleaning up expired cache entries

## User vs daemon threads

| Feature          | User thread                         | Daemon thread                         |
| ---------------- | ----------------------------------- | ------------------------------------- |
| **Purpose**      | Core application logic              | Background support services           |
| **JVM priority** | High—JVM waits for them to finish   | Low—JVM ignores during shutdown       |
| **Lifecycle**    | Independent                         | Dependent on user threads             |
| **JVM exit**     | Program keeps running if one exists | Program exits if only daemons remain  |
| **Inheritance**  | Inherits "user" status from parent  | Inherits "daemon" status from parent  |

## Creating a daemon thread

Call `setDaemon(true)` **before** calling `start()`. Calling it after throws
`IllegalThreadStateException`.

```java
Thread backgroundTask = new Thread(() -> {
    while (true) {
        System.out.println("Supporting user tasks...");
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
    }
});

backgroundTask.setDaemon(true);
backgroundTask.start();

System.out.println("Main thread is finishing.");
// Once main ends, the daemon is abruptly killed
```

## Critical warnings

**Abrupt termination:** When the last user thread ends, the JVM shuts down
immediately. Daemon threads stop in their tracks; `finally` blocks may not
execute, and stacks are not unwound.

**I/O hazard:** Never use a daemon thread for tasks that write to files or
databases. They can be killed mid-execution, risking corrupted files or hanging
database connections.

**Silent exit:** There is no graceful shutdown for a daemon. Work in progress is
simply lost.
