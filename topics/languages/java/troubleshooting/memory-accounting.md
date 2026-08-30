# Memory accounting

A Java process exposes memory through several measurement layers. The Java
Virtual Machine (JVM) reports what its memory pools use or commit, while the
operating system reports which process pages occupy physical memory. Memory
accounting aligns those measurements over time to find the component that
grows with the process.

> **Compare changes measured over the same interval; do not force JVM
> commitments and operating-system residency into one exact total.**

## Keep memory states separate

The JVM can reserve a virtual address range without using physical memory for
every page. It can then commit part of that range for use and occupy some of
the committed capacity with objects or runtime structures.

These states answer different questions:

| Measurement                 | Question it answers                              |
|-----------------------------|--------------------------------------------------|
| Reserved address space      | What virtual range is set aside?                 |
| Committed memory            | What capacity is guaranteed to the JVM?          |
| Used memory                 | What does this JVM memory pool mark as occupied? |
| Resident Set Size (RSS)     | Which process pages are in physical memory?      |
| Proportional Set Size (PSS) | What share of resident pages belongs here?       |

Within one JVM memory pool, used memory cannot exceed committed memory, and
committed memory cannot exceed a defined maximum:

```text
used <= committed <= maximum
```

Used heap is not the same as live heap. It can include unreachable objects
that garbage collection (GC) has not reclaimed. The **live set** is the
reachable heap that remains after GC has evaluated the relevant regions.

RSS belongs to a different accounting layer. It includes resident heap pages,
native allocations, shared libraries, and file mappings. A committed page may
not be resident, while a resident mapped page may not belong to a JVM memory
pool. RSS therefore does not belong in the JVM inequality above.

## Start with the outside measurement

First record the memory limit and the measurement that can cross it. On Linux,
`ps` reports RSS in kibibytes. Replace `<pid>` with the operating-system
process identifier of the running JVM:

```bash
ps -o pid,rss,vsz,cmd -p <pid>
```

The command also reports **virtual size (VSZ)**, the complete mapped virtual
address space. Large reserved ranges can make VSZ enormous without consuming
the same amount of physical memory, so VSZ cannot substitute for RSS.

For a process running in a container, record the control-group usage and
limit. A **control group** accounts for a configured set of processes and may
also charge file-backed memory. Its total can therefore differ from one
process's RSS.

On Linux, `/proc` separates resident memory by mapping type:

```bash
cat /proc/<pid>/smaps_rollup
```

The report includes anonymous, file-backed, and shared resident pages. RSS
counts a shared page in every process that maps it. PSS divides that page
among those processes, making it a better ownership estimate for shared
libraries and mappings.

Every snapshot needs its context:

```text
process identifier
timestamp
workload level
process RSS and PSS
container usage and limit, if applicable
```

Without that context, an RSS sample from peak traffic and a JVM sample from an
idle period create a discrepancy that never existed at one moment.

## Add the JVM measurements

The Java Development Kit includes `jcmd`, a diagnostic utility that can query
a running JVM owned by the same operating-system user. Start with the heap:

```bash
jcmd <pid> GC.heap_info
```

This reports heap configuration and current occupancy. The maximum heap,
often configured with `-Xmx`, is only a ceiling. It is neither current usage
nor the process memory limit.

The heap command leaves the JVM's runtime allocations unexplained. On HotSpot
JVMs, **Native Memory Tracking (NMT)** groups those allocations by subsystem.
NMT must begin collecting when the JVM starts:

```text
-XX:NativeMemoryTracking=summary
```

Request the report in one unit:

```bash
jcmd <pid> VM.native_memory summary scale=MB
```

NMT reports reserved and committed memory for categories such as the heap,
classes, threads, compiled code, GC, and the compiler. It does not fully track
third-party native code, some Java Development Kit library allocations, or
file-backed mappings. Enabling it also adds overhead, so production use needs
an operational decision.

Add metrics for important allocations outside that ledger. JVM buffer-pool
metrics report the count and native payload capacity of direct byte buffers.
The `/proc` measurements already captured resident file mappings.

When growth matters, establish a baseline after startup and warmup:

```bash
jcmd <pid> VM.native_memory baseline
```

Run the representative workload for the observation interval, then request
the change:

```bash
jcmd <pid> VM.native_memory summary.diff scale=MB
```

## Build a change worksheet

Convert the values to one display unit and put measurements from the same
process and interval beside one another. Do not add them as if they were
disjoint resident regions:

```text
Observation interval: 10:00 -> 10:30

process RSS change                  +2,400 MB
post-GC heap change                   +100 MB
NMT Thread committed change            +20 MB
NMT Class committed change              +5 MB
direct-buffer capacity change          +90 MB
resident file-mapping PSS change    +2,050 MB
```

The values need not sum exactly because they describe different states and
can overlap. Their movement still answers the useful question: which signal
grew at roughly the same time and scale as RSS?

In this example, the post-GC heap and NMT categories remain nearly stable
while resident file mappings grow by about two gigabytes. The mapping trend
is the strongest next lead; the committed Java heap is not subtracted from
RSS to manufacture an unexplained remainder.

## Let the growing signal choose the next question

Each pattern narrows the investigation:

| Signal that grows with RSS      | Next ownership question                 |
|---------------------------------|-----------------------------------------|
| Post-GC heap                    | Which Java objects remain reachable?    |
| Stable heap with costly GC      | Which code creates temporary objects?   |
| NMT Thread                      | Why are thread count or stacks growing? |
| NMT Class                       | Why do classes or class loaders remain? |
| Direct-buffer capacity          | Who owns the buffers or pool capacity?  |
| Resident mapping RSS or PSS     | Which mapped files became resident?     |
| RSS with no matching JVM signal | Which native library allocated memory?  |

Use progressively stronger evidence. If the heap grows, a class histogram
gives object counts and bytes by class before the more expensive step of
capturing every object and reference in a heap dump. If an NMT category grows,
inspect its category-specific metric. If RSS grows without a JVM signal,
inspect operating-system maps and then native allocation paths.

```text
process and container measurements
                |
                v
heap trend and NMT changes
                |
                v
category-specific metric
                |
                v
heap dump, mapping detail, or native profile
```

Stop when one explanation accounts for the observed growth. More invasive
evidence should answer a remaining question, not repeat a conclusion that a
cheaper measurement already supports.

## Preserve measurements that require preparation

Some evidence cannot be reconstructed after the process exits. NMT must be
enabled at startup. GC logging preserves heap transitions, and a rolling Java
Flight Recorder captures recent JVM and application events. Automatic heap
dump configuration can preserve the object graph for supported heap failures.

The dump destination needs enough free space and must survive process or
container replacement. External kills and native resource failures still
require operating-system, container, and runtime evidence.

Memory accounting succeeds when time-aligned measurements identify a growing
region and produce one specific ownership question. Profile that region, not
the entire process.

---

Return to [Troubleshooting](_index.md)
