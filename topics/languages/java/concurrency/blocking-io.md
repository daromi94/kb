# Blocking I/O

When a thread initiates a blocking I/O operation—reading from a socket,
writing to disk—it relinquishes the CPU and enters a wait state until the
operation completes. The thread cannot perform any other logic while I/O is
pending. Concurrency provides throughput gains by overlapping this blocked
time with productive work on other threads.

## Execution lifecycle

When a Java application calls `inputStream.read()`, the following occurs:

1. **System call:** The JVM invokes a native method that triggers a system
   call (e.g., `read()`) to the OS kernel
2. **Thread suspension:** The kernel moves the thread from Running to
   Waiting and removes it from the CPU scheduling queue
3. **Kernel I/O:** The kernel's I/O subsystem interacts with the hardware
   (e.g., waiting for data at a network interface card)
4. **Kernel buffer copy:** The hardware receives data and the kernel copies
   it from the hardware buffer into the kernel's internal buffer
5. **User-space transfer:** Data is copied from the kernel buffer into the
   application's buffer (the byte array in Java code)
6. **Resumption:** The kernel marks the thread as Runnable. The scheduler
   puts it back on the CPU and `read()` returns

## Overlapping execution

On a single-processor system, true parallelism is impossible. But when one
thread blocks on I/O, the OS scheduler context-switches to another thread,
reclaiming the idle cycles.

Consider two tasks on a single core:

- Task A: 50ms CPU + 50ms I/O
- Task B: 50ms CPU

Serial execution takes **150ms**. With concurrency, Task B's CPU work runs
during Task A's I/O wait, finishing in **100ms**.

```
Serial:
  [A cpu 50ms][A io 50ms][B cpu 50ms]  = 150ms

Concurrent (single core):
  [A cpu 50ms][B cpu 50ms]
              [A io 50ms ]             = 100ms
```

## Scalability constraints

Blocking I/O creates a strict **1:1 mapping** between active requests and
threads.

**Stack memory:** 1,000 concurrent users waiting for database results require
1,000 threads. At the default 1MB stack size, that is ~1GB of RAM consumed by
thread overhead alone, regardless of actual work.

**Context switch overhead:** As thread count grows, the CPU spends a higher
proportion of time saving and loading thread contexts rather than executing
application logic. If I/O operations are extremely fast (e.g., NVMe cache
hits), the switching cost may exceed the overlap benefit.

**Liveness risks:** If a second thread is waiting for a resource held by the
blocked thread, the system still reaches a standstill.

## Blocking vs. non-blocking

| Feature         | Blocking I/O                  | Non-blocking I/O                    |
|-----------------|-------------------------------|-------------------------------------|
| Thread state    | Suspended until data is ready | Remains active, returns immediately |
| Data transfer   | Kernel copies to user space   | App must poll or await notification |
| Code complexity | Low, straightforward          | High, requires selectors/callbacks  |
| Best suited for | Long-lived heavy connections  | Many short-lived chatty connections |

## Related

- [Concurrency](concurrency.md) - Why overlapping tasks improves throughput
- [Thread memory](thread-memory.md) - Thread-private stack and shared heap
- [Thread pool sizing](thread-pool-sizing.md) - Sizing pools for I/O-bound workloads

---

Return to [Concurrency](_index.md)
