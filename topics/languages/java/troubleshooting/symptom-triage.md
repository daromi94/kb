# Symptom triage

A Java memory symptom can originate in the managed heap, elsewhere in the
process, or at an external memory limit. Triage first identifies which layer
reported the problem and which region is growing. Only then can a diagnostic
artifact answer the right question.

> **Classify the failure before choosing the diagnostic tool.**

## Establish the process boundary

The **Java Virtual Machine (JVM)** runs inside an operating-system process.
The Java heap is one memory region within that process, not its complete
footprint.

**Garbage collection (GC)** manages ordinary Java objects in the heap. Once
the application can no longer reach an object, GC can reclaim its heap space.
It does not manage the other process regions:

| Region         | What consumes memory                         |
|----------------|----------------------------------------------|
| Java heap      | Ordinary Java objects                        |
| Class metadata | Runtime information about loaded classes     |
| Thread stacks  | Method calls and local state for each thread |
| Direct buffers | Native payloads reached through Java objects |
| JVM runtime    | Collector, compiler, and compiled code       |
| Other native   | Libraries, allocators, and file mappings     |

This boundary determines whether Java-object evidence can explain the
symptom:

```text
large process
     |
     +--> heap grows --------> investigate Java objects
     |
     +--> heap stays stable -> investigate other process memory
```

## First determine who reported the failure

Start with the evidence produced when the symptom occurred. A Java error, a
fatal-error file, and an operating-system kill describe different failure
boundaries.

An `OutOfMemoryError` reports resource exhaustion or failure to make useful
progress under memory pressure. Its detail text usually identifies the failed
request or condition. Common message fragments include:

| Message fragment                          | Failed request                          |
|-------------------------------------------|-----------------------------------------|
| `Java heap space`                         | Space for another heap object           |
| `GC overhead limit exceeded`              | GC time with too little space recovered |
| `Requested array size exceeds VM limit`   | Array larger than the JVM permits       |
| `Metaspace`                               | Space for loaded-class metadata         |
| `Compressed class space`                  | Encoded class-metadata address space    |
| `Cannot reserve ... direct buffer memory` | Native payload for a direct buffer      |
| `unable to create new native thread`      | Memory or system limit for a thread     |

The list is not exhaustive. Preserve the complete message and stack trace
rather than matching only one phrase.

The message identifies the failing boundary, not why the condition arose. For
example, `Java heap space` can result from retained objects, an undersized
heap, or one request that creates an unusually large object graph.

If the process exits without an `OutOfMemoryError`, look outside the Java
exception path:

```text
Java error and stack trace
        -> JVM or Java library rejected a resource request

fatal-error file
        -> JVM or native code encountered a fatal failure

kernel or container kill event
        -> process crossed an externally enforced limit
```

The JVM commonly writes a fatal-error file named `hs_err_pid*.log` after a
fatal runtime or native-code failure. An operating-system or container kill
may leave no Java exception because the decision occurs outside the JVM.

If the process has exited, preserve these artifacts before restarting it.
Measurements that require attaching to the live JVM are no longer available.

## For a live process, observe what GC leaves behind

Raw heap occupancy rises as the application creates objects and falls as GC
reclaims them:

```text
used heap
   ^       /|      /|      /|
   |      / |     / |     / |
   |_____/  |____/  |____/  |____> time
              GC      GC
```

The **live set** is the reachable data that remains after GC has evaluated the
relevant heap regions. A young-generation collection examines only part of
the heap, so not every post-GC sample represents the whole live set. Compare
measurements with the same collection scope under equivalent workload.

Two trends lead in different directions:

```text
stable live set:   800 MB -> 820 MB -> 790 MB -> 810 MB

growing live set:  800 MB -> 1.1 GB -> 1.5 GB -> 2.0 GB
```

A growing live set points toward retained objects or a growing workload. A
stable live set with costly, frequent GC can indicate **allocation churn**:
the application creates and discards short-lived objects at a high rate. It
can also indicate that the heap or one of its generations is too small.

Growth alone does not prove a leak. Cache warmup, increased traffic, and
delayed cleanup can raise the live set legitimately. A retention diagnosis
must identify an owner that keeps objects longer than intended.

## Compare the heap trend with process memory

**Resident Set Size (RSS)** counts the process pages currently in physical
memory according to the operating system. RSS includes the Java heap, native
allocations, shared libraries, and resident file mappings.

Compare trends over the same interval instead of subtracting JVM commitments
from RSS. The JVM can commit memory without making every page resident, while
RSS can count shared or mapped pages that do not belong to the heap.

| Post-GC heap trend | RSS trend         | Likely direction              |
|--------------------|-------------------|-------------------------------|
| Rising             | Rises similarly   | Heap retention or workload    |
| Stable             | Rising            | Memory outside the Java heap  |
| Stable             | Stable; GC costly | Allocation churn or heap size |
| Rising             | Rises much faster | Multiple contributors         |

The table identifies a direction, not a proof. Time-aligned measurements are
more useful than exact equality between numbers from different accounting
layers.

## Choose evidence that answers the remaining question

Each diagnostic artifact answers one kind of question:

**Java Flight Recorder** records JVM and application events on one timeline.
On HotSpot JVMs, **Native Memory Tracking** groups the JVM's own allocations
into runtime categories. Both observe a live process; Native Memory Tracking
must be enabled when the JVM starts.

| Question                            | First evidence                                    |
|-------------------------------------|---------------------------------------------------|
| Which layer reported the failure?   | Java, runtime, kernel, or container logs          |
| Does the heap recover after GC?     | GC log or Java Flight Recorder timeline           |
| Which classes occupy the heap?      | Class histogram: object counts and bytes by class |
| What keeps those objects alive?     | Heap dump: objects and references between them    |
| Which JVM-native region is growing? | Native Memory Tracking categories                 |
| Which code creates temporary data?  | Allocation profile grouped by method-call path    |
| What lies outside JVM accounting?   | OS maps and native allocation profile             |

The complete triage path is:

```text
memory symptom
      |
      +--> process exited
      |         |
      |         +--> Java error, fatal-error file, or external kill evidence
      |
      +--> process alive
                |
                +--> live set grows -------> retention evidence
                |
                +--> live set stable,
                |    GC remains costly ----> allocation evidence
                |
                +--> RSS grows while
                     heap stays stable ----> native-memory evidence
```

Start with the reporting boundary, locate the growing region, and collect only
the artifact that can explain its ownership or activity.

---

Return to [Troubleshooting](_index.md)
