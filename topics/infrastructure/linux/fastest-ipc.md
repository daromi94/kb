# Fastest IPC

For two processes on the same machine, the fastest general-purpose
interprocess communication (IPC) mechanism is usually shared memory. It lets
both processes access the same physical memory pages directly.

With a pipe or socket, data typically moves through the kernel:

```text
+------------------+
| Process A memory |
+--------+---------+
         | copy
         v
+------------------+
| Kernel buffer    |
+--------+---------+
         | copy
         v
+------------------+
| Process B memory |
+------------------+
```

With shared memory, both processes map the same pages:

```text
              +------------------+
              | Physical RAM     |
              | shared pages     |
              +--------+---------+
                       ^
                  map / \ map
                     /   \
                    /     \
          +--------+       +---------+
          |                          |
+---------+---------+      +---------+---------+
| Process A mapping |      | Process B mapping |
+-------------------+      +-------------------+
```

Once the mappings exist, communication can become ordinary loads and stores.
The mappings may use different virtual addresses while still referring to the
same physical page:

```text
Process A virtual memory        Process B virtual memory

0x70000000 --------+          0x90000000 --------+
                   |                             |
                   +------ physical page --------+
```

If process A writes:

```c
shared->value = 42;
```

process B can subsequently read:

```c
printf("%d\n", shared->value);
```

The value does not need to pass through a kernel buffer.

## Why shared memory is fast

> **The fastest data transfer is often no data transfer at all.**

Shared memory avoids kernel-mediated payload copies when the producer creates
data directly in the shared region. If the data starts in private memory,
copying or serializing it into the shared region still counts as a payload
copy.

The steady-state paths differ in both copying and kernel involvement:

| IPC mechanism                | Payload copies             | Kernel work per message | Typical performance |
|------------------------------|----------------------------|-------------------------|---------------------|
| TCP loopback socket          | Usually multiple           | High                    | Slower              |
| Unix domain socket           | Usually multiple           | High                    | Fast                |
| Pipe                         | Usually multiple           | High                    | Fast                |
| Shared memory                | Zero for direct production | Very low                | Fastest             |
| Shared memory + busy polling | Zero for direct production | Almost none             | Extremely fast      |

The kernel still establishes the shared region, but it need not participate in
every message. Linux APIs used to set up shared mappings include:

```c
shm_open()
mmap()
```

and:

```c
memfd_create()
mmap()
```

After setup, the steady-state communication path can remain in userspace.

## Shared memory needs a communication protocol

Shared memory is IPC, but it solves only the storage part of the protocol. A
complete design answers two separate questions:

```text
1. Where is the data shared?
2. How does the other process detect new data?
```

Shared pages answer the first question. Synchronization and notification
answer the second.

For example, shared storage can contain both a payload and queue metadata:

```text
shared memory
    |
    +-- payload
    +-- write_index
    +-- read_index
```

A ring buffer is a common high-performance design:

```text
                  shared memory

             read                write
              |                    |
              v                    v
       +------+------+------+------+------+
       | M1   | M2   | M3   |      |      |
       +------+------+------+------+------+
```

The producer writes directly into the shared buffer, then publishes the new
write position. The consumer observes that position and reads the payload from
the same buffer.

```text
+----------+     write payload     +--------------------+
| Producer | --------------------> | Shared ring buffer |
+----------+                       +---------+----------+
                                             |
                                             | read payload
                                             v
                                   +---------+----------+
                                   | Consumer           |
                                   +--------------------+
```

No kernel buffer carries the payload between the processes.

## The data path becomes cache coherence

At very high performance levels, IPC stops being primarily a syscall problem
and becomes a CPU-cache problem. If the processes run on different cores, each
core may cache the shared lines locally:

```text
+------------------+                 +------------------+
| Core 0           |                 | Core 1           |
| Process A        |                 | Process B        |
| L1 cache         |                 | L1 cache         |
+--------+---------+                 +---------+--------+
         |                                     |
         +------- cache coherence -------------+
                       |
                       v
                 +-----+-----+
                 | Memory    |
                 +-----------+
```

When process A modifies a shared cache line, the cache-coherence system makes
the new line state available to the core running process B. Communication then
resembles:

```text
store
  |
  v
cache coherence
  |
  v
load
```

rather than:

```text
write syscall
  |
  v
kernel work
  |
  v
buffer copy
  |
  v
scheduler wakeup
  |
  v
read syscall
  |
  v
buffer copy
```

## Synchronization establishes visibility

Naively sharing memory is unsafe. Consider a message with a readiness flag and
a payload:

```c
struct Message {
    int ready;
    char payload[1024];
};
```

Writing the fields in source order does not create a portable publication
protocol:

```text
payload = ...
ready = 1;
```

Compilers and CPUs may reorder memory operations. High-performance
shared-memory IPC therefore uses atomic variables, memory barriers,
release/acquire semantics, locks, or carefully designed lock-free queues.

A release store publishes the completed payload. An acquire load that observes
that store makes the preceding writes visible to the consumer:

```text
producer:
    write payload
    ready.store(true, release)

consumer:
    if ready.load(acquire):
        read payload
```

The acquire/release pair establishes the necessary visibility ordering.

## Busy polling removes wakeup latency

A consumer can wait with a blocking primitive such as a futex, event file
descriptor, semaphore, or condition variable. Blocking conserves CPU time but
introduces kernel and scheduler wakeup latency.

An ultra-low-latency consumer may busy-spin instead:

```c
while (!message_ready()) {
    cpu_relax();
}
```

Busy polling keeps the steady-state path in userspace:

```text
busy polling
    |
    +-- very low latency
    |
    +-- high CPU consumption
```

Blocking makes the opposite tradeoff:

```text
blocking wait
    |
    +-- low CPU consumption
    |
    +-- higher wakeup latency
```

This tradeoff appears in trading systems, databases, packet-processing
systems, and high-performance runtimes.

## A low-latency architecture

A fast steady-state design places both data and metadata in a shared ring
buffer:

```text
Process A                                      Process B
+------------------+                          +------------------+
| Producer         |                          | Consumer         |
|                  |                          |                  |
| write payload    |                          |                  |
+--------+---------+                          +---------+--------+
         |                                              ^
         v                                              |
 +-------+----------------------------------------------+-------+
 | Shared ring buffer                                           |
 |                                                              |
 | data | write_position | read_position | sequence numbers     |
 +-------+----------------------------------------------+-------+
         |                                              ^
         | publish write position                       | read payload
         +----------------------------------------------+
```

The producer writes a payload and updates an atomic write position. The
consumer observes the position and reads the payload. No syscall is required
for this steady-state data path.

## Latency and throughput favor different designs

Shared memory is usually the fastest IPC mechanism, but the best design depends
on what "fastest" means.

Lowest latency favors:

```text
shared memory
    + lock-free queue
    + busy polling
    + CPU pinning
    + NUMA-aware placement
```

Highest throughput favors:

```text
shared memory
    + batching
    + large ring buffers
```

Simplicity with good performance favors:

```text
Unix domain sockets
```

Unix domain sockets are easier to use correctly while remaining fast. They
provide kernel-managed buffering, blocking, access control, and stream or
message semantics without a custom shared-state protocol.

## Why Unix domain sockets are slower

A Unix domain socket sends data through kernel-managed socket buffers:

```text
+-----------+
| Process A |
+-----+-----+
      | send()
      v
+-----+----------------+
| Kernel socket buffer |
+-----+----------------+
      | recv()
      v
+-----+-----+
| Process B |
+-----------+
```

This path requires system calls, kernel bookkeeping, and usually payload
copies. Shared memory replaces that path with loads and stores:

```text
+-----------+
| Process A |
+-----+-----+
      | store
      v
+-----+-------+
| Shared page |
+-----+-------+
      | load
      v
+-----+-----+
| Process B |
+-----------+
```

That difference is fundamental.

## Share ownership instead of data

The highest-performance systems often avoid moving large objects entirely.
Instead of copying a 1 MiB message from one process to another, they allocate
the payload in a shared memory pool:

```text
shared memory pool

buffer 812
+------------------------------+
| 1 MiB payload                |
+------------------------------+

queue message
+------------------------------+
| buffer_id = 812              |
+------------------------------+
```

Only the small descriptor crosses the queue. The consumer accesses the same
underlying buffer, then returns ownership according to the pool's lifetime and
reclamation rules.

This pattern appears in DPDK, Apache Arrow, shared-memory databases,
packet-processing frameworks, and high-performance remote procedure call
(RPC) systems. The general principle is:

```text
Do not move the bytes.
Move ownership or references to the bytes.
```

### Mental model

The performance hierarchy is roughly:

```text
network socket
      |
      v
TCP loopback
      |
      v
Unix domain socket or pipe
      |
      v
shared memory + blocking synchronization
      |
      v
shared memory + lock-free queue
      |
      v
shared memory + lock-free queue + busy polling
```

At the lowest-latency end of this hierarchy, IPC barely resembles traditional
message passing. It becomes two CPU cores communicating through cache-coherent
shared memory, coordinated by an explicit synchronization protocol.

---

Return to [Linux](_index.md)
