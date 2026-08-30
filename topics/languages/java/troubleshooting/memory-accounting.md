# Memory accounting

Memory accounting explains a Java process by reconciling the operating
system's measurement with measurements from the Java Virtual Machine (JVM).
The result is a budget that shows which region deserves investigation.

The central rule is:

> **Do not call memory unexplained until you have compared measurements that
> describe the same process at the same time.**

## Four measurements describe different things

A Java process can reserve address space without occupying all of it. It can
also commit memory without touching every page. Four terms keep those states
separate:

- **Reserved memory** is virtual address space set aside for possible use.
- **Committed memory** is memory the JVM can use without first requesting
  more backing from the operating system.
- **Used memory** contains live data or runtime structures at that moment.
- **Resident Set Size (RSS)** is the process memory currently resident in
  physical memory according to the operating system.

These values answer different questions:

```text
reserved >= committed >= used

RSS = resident pages from heap, native allocations, mappings, and libraries
```

RSS is not expected to equal any one JVM number. Some committed pages may not
be resident, and file-backed or shared mappings may appear in RSS without
belonging to the Java heap.

## Start with the outside measurement

Measure the process from the operating system or its container runtime first.
On Linux, a process listing reports RSS in kibibytes (KiB), where one KiB is
1,024 bytes:

```bash
ps -o pid,rss,vsz,cmd -p <pid>
```

**Virtual size (VSZ)** is the process's mapped virtual address space. Large
reserved regions can make VSZ much larger than physical memory, so VSZ is not
a useful substitute for RSS.

For a container, also record its memory usage and limit. A container limit
applies to a **control group**, which accounts for and limits a set of
processes. The control-group total may not match one process's RSS.

The first snapshot should therefore record:

```text
process RSS
container usage, if applicable
container or host limit
timestamp and workload level
```

The timestamp matters because memory changes while commands run. Comparing an
RSS sample from peak traffic with a JVM sample from an idle period creates a
false discrepancy.

## Add the JVM's internal ledger

The JVM exposes heap information through `jcmd`, a diagnostic command that
attaches to a running JVM owned by the same operating-system user.

```bash
jcmd <pid> GC.heap_info
```

This reports the heap configuration and current occupancy. The maximum heap,
often configured with `-Xmx`, is a ceiling. It is not a promise that the
process uses that amount, and it is not the process's total memory limit.

The heap explains only one part of the JVM. On a HotSpot-based JVM, **Native
Memory Tracking (NMT)** groups the runtime's own native allocations by
subsystem. Because collection begins at startup, enable it when the JVM starts:

```text
-XX:NativeMemoryTracking=summary
```

Once enabled, request a summary in a consistent unit:

```bash
jcmd <pid> VM.native_memory summary scale=MB
```

The report separates categories such as:

| NMT category | Typical contents                              |
|--------------|-----------------------------------------------|
| Java Heap    | Reserved and committed managed heap           |
| Class        | Metaspace and class-related structures        |
| Thread       | Thread stacks and thread metadata             |
| Code         | Compiled machine code and code-cache metadata |
| GC           | Collector data structures                     |
| Compiler     | Just-in-time compiler state                   |
| Internal     | Other JVM runtime allocations                 |

NMT is the JVM ledger, not the process ledger. It does not fully track
third-party native libraries, every Java standard-library allocation, or
file-backed mappings. Enabling it also has a performance cost, so production
use requires an explicit operational decision.

## Build an approximate budget

Normalize every measurement to one unit and write down each contributor. A
budget makes the unexplained difference visible:

```text
Observed process RSS:                        8,200 MB

JVM and application contributors:
  committed Java heap                        4,096 MB
  class metadata                               260 MB
  thread stacks and metadata                   480 MB
  code cache and compiler                      230 MB
  GC and other JVM structures                  420 MB
  direct buffers from buffer-pool metrics    1,100 MB
  identified resident file mappings            900 MB
                                                -----
Approximate explained memory                 7,486 MB
Approximate unexplained difference             714 MB
```

The budget is a reconciliation, not an exact accounting identity. Categories
can overlap at different measurement layers, RSS counts only resident pages,
and native allocators may retain partly used pages. That last condition is
called **allocator fragmentation**.

Its purpose is narrower: identify whether the discrepancy is tens of
megabytes or several gigabytes, and determine which branch can explain it.

## Interpret the shape of the budget

The largest contributor determines the next question:

| Budget shape                     | Next investigation                    |
|----------------------------------|---------------------------------------|
| Used heap grows after collection | Object retention                      |
| Stable heap; GC is frequent      | Allocation rate                       |
| Thread category grows            | Thread count and effective stack size |
| Class category grows             | Class loading and loader lifetime     |
| Direct-buffer metrics grow       | Buffer ownership and pool limits      |
| RSS grows while NMT stays stable | Mappings, native libraries, allocator |

Take repeated snapshots under comparable load when growth matters. NMT can
store a baseline and report the change since that point:

```bash
jcmd <pid> VM.native_memory baseline
jcmd <pid> VM.native_memory summary.diff scale=MB
```

A difference report answers a better question than a single large number:
which JVM-native category grew during the observation window?

## Use progressively stronger evidence

Start with broad summaries and stop when one explanation accounts for the
symptom.

```text
RSS and container limit
          |
          v
heap information + NMT summary
          |
          v
class histogram or category-specific metric
          |
          v
heap dump, OS maps, or native allocation profile
```

Before capturing the complete object graph, use a **class histogram** to see
which classes dominate the current heap. It groups objects by class and
reports their counts and shallow byte totals:

```bash
jcmd <pid> GC.class_histogram
```

A histogram shows composition, not ownership. If a suspicious class needs an
ownership explanation, collect a heap dump so the references between objects
can be traced. If the unexplained difference remains outside the JVM's ledger,
move to operating-system maps or native profiling instead.

## Preserve evidence before failure

Several diagnostics require preparation. NMT cannot be enabled after startup,
and a failure may remove the process before an operator can attach.

Preserve heap history with **unified GC logging**, which records collections
and heap transitions. For broader context, **Java Flight Recorder (JFR)** can
retain recent JVM and application events in a bounded ring. As new events
arrive, the ring overwrites events outside its size or time window.

| Preparation                        | Evidence preserved                |
|------------------------------------|-----------------------------------|
| `-XX:NativeMemoryTracking=summary` | JVM native-memory categories      |
| `-XX:+HeapDumpOnOutOfMemoryError`  | Heap at Java heap exhaustion      |
| `-XX:HeapDumpPath=<path>`          | Controlled dump destination       |
| Unified GC logging                 | Heap and collection behavior      |
| Continuous Flight Recorder ring    | Recent JVM and application events |

The dump path needs enough free space and must survive process or container
replacement. Heap-dump-on-error does not capture resource failures outside
Java heap exhaustion, so external logs and runtime events remain necessary.

Memory accounting succeeds when the numbers support a specific next question:

```text
total footprint
      -
explained contributors
      =
small, named uncertainty
```

Build the budget first. Profile only the region that the budget leaves
unexplained.

---

Return to [Troubleshooting](_index.md)
