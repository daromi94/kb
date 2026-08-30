# Symptom triage

Memory troubleshooting starts by identifying which part of the Java process
is under pressure. A **heap dump** records Java objects and their references,
but it cannot explain every way a process consumes memory.

The central rule is:

> **Classify the failure before choosing the diagnostic tool.**

## A Java process has several memory regions

The **Java Virtual Machine (JVM)** runs Java code inside an operating-system
process. That process contains the managed Java heap and several kinds of
memory outside it.

| Region        | What it contains                               |
|---------------|------------------------------------------------|
| Java heap     | Objects managed by garbage collection          |
| Metaspace     | Loaded class metadata                          |
| Thread stacks | Method frames and local state for each thread  |
| Direct memory | Native buffers used through Java APIs          |
| JVM native    | Garbage collector, compiler, and runtime state |
| Other native  | Libraries, allocators, and file mappings       |

**Garbage collection (GC)** finds Java objects that the application can no
longer reach and reclaims their heap space. It manages the Java heap, not the
entire process.

This boundary explains a common diagnostic failure:

```text
large process
     |
     +--> large Java heap  --> inspect Java objects
     |
     +--> large non-heap   --> inspect native memory and mappings
```

## First question: did the JVM report the failure?

An `OutOfMemoryError` means the JVM could not satisfy a particular resource
request. Its detail message identifies the failed request and provides the
first branch in the investigation.

| Detail message                       | Failed resource              |
|--------------------------------------|------------------------------|
| `Java heap space`                    | Space for another object     |
| `GC overhead limit exceeded`         | Useful progress during GC    |
| `Metaspace`                          | Space for class metadata     |
| `Direct buffer memory`               | Space for a direct buffer    |
| `unable to create new native thread` | Resources for another thread |

The message identifies where allocation failed. It does not prove why that
region filled. A heap can fill because the application retains objects, the
configured maximum is too small, or one request creates an unusually large
group of connected objects.

If the process disappears without a Java error, inspect the evidence outside
the JVM. The operating system or a container runtime may terminate a process
that exceeds its memory limit.

```text
Java error and stack trace
        -> JVM detected resource exhaustion

kernel or container kill event
        -> process exceeded an external limit

fatal-error file
        -> JVM or native code crashed
```

The JVM writes a **fatal-error file**, commonly named `hs_err_pid*.log`, when
it detects a fatal runtime or native-code crash.

An external kill concerns the process's total footprint. The Java heap,
thread stacks, native libraries, and mapped files can all contribute.

## Second question: what remains after collection?

For a process that is still running, raw heap usage is noisy. Heap occupancy
rises as objects are allocated and falls when GC reclaims unreachable
objects.

```text
used heap
   ^       /|      /|      /|
   |      / |     / |     / |
   |_____/  |____/  |____/  |____> time
              GC      GC
```

The **live set** is the heap occupied by reachable objects after a collection.
It gives a more useful signal than the peak immediately before GC.

Compare the live set across equivalent workload periods:

```text
stable live set:    800 MB -> 820 MB -> 790 MB -> 810 MB

growing live set:   800 MB -> 1.1 GB -> 1.5 GB -> 2.0 GB
```

A stable live set with frequent collections points toward allocation churn:
the application creates many short-lived objects. A growing live set points
toward retention or a growing workload. A heap dump can reveal what keeps
those objects reachable.

Growth alone does not prove a leak. Cache warming, larger traffic volume, and
delayed cleanup can all increase the live set. The investigation must connect
the growth to an owner that retains the objects longer than intended.

## Third question: does the heap explain the process?

**Resident Set Size (RSS)** is the physical memory currently resident for the
process according to the operating system. RSS includes more than the Java
heap.

Compare RSS with the JVM's memory measurements:

```text
RSS:                         8 GB
committed Java heap:         3 GB
other explained JVM memory:  2 GB
unexplained difference:      3 GB
```

A large difference directs the investigation outside the heap. Start with
**Native Memory Tracking (NMT)**, the JVM's accounting of its own native
allocations. If NMT does not explain the difference, compare direct-buffer
count and capacity, thread counts, and operating-system memory maps with RSS.
A memory map identifies the address regions assigned to the process and the
files that back them.

The two measurements produce four useful cases:

| Post-GC heap | RSS relationship  | Likely direction      |
|--------------|-------------------|-----------------------|
| Rising       | Heap explains RSS | Heap retention        |
| Stable       | Heap explains RSS | Heap sizing or churn  |
| Stable       | RSS much larger   | Native memory or maps |
| Rising       | RSS much larger   | Multiple contributors |

## Choose the first tool from the question

Each tool answers a different question. Start with the least invasive source
that can distinguish the remaining explanations.

| Question                              | Evidence                      | What it reveals                         |
|---------------------------------------|-------------------------------|-----------------------------------------|
| Why did the process exit?             | Error, kernel, or runtime log | Which layer reported the failure        |
| Is the live set growing?              | GC log or Flight Recorder     | Heap changes and related runtime events |
| Which classes occupy the heap?        | Class histogram               | Object counts and shallow sizes         |
| What retains those objects?           | Heap dump and Memory Analyzer | Reference paths from objects to roots   |
| Which JVM-native category is growing? | Native Memory Tracking        | JVM allocation categories               |
| Which code creates short-lived data?  | Allocation profile            | Allocation volume by call path          |
| What lies outside JVM accounting?     | OS maps and native profile    | Mappings and native allocation paths    |

The diagnostic path is therefore:

```text
failure or memory symptom
          |
          v
identify the reporting boundary
          |
          v
compare post-GC heap with RSS
          |
          +--> heap retention --> heap dump
          |
          +--> allocation rate --> allocation profile
          |
          +--> non-heap growth --> native accounting
```

Start with the symptom, locate the memory region, and only then collect the
artifact that can explain ownership.

---

Return to [Troubleshooting](_index.md)
