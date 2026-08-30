# Off-heap diagnostics

The Java heap is only one part of a **Java Virtual Machine (JVM)** process.
Thread stacks, class metadata, direct buffers, memory-mapped files, and native
libraries can make the process consume far more physical memory. Diagnose the
difference by following the component that grows over the same time interval.

> **Measure physical memory from outside the process, classify allocations
> from inside it, and profile only the growth neither view explains.**

## Separate memory commitments from residency

**Garbage collection (GC)** manages the Java heap, where ordinary Java
objects live. Once the application can no longer reach an object, GC can
reclaim its heap space. It cannot reclaim thread stacks, direct buffers,
mapped files, or native-library allocations. Together, those process regions
make up **off-heap memory**.

Off-heap memory is a boundary, not one region:

| Mechanism        | What consumes memory                         |
|------------------|----------------------------------------------|
| JVM runtime      | Collector, compiler, and compiled-code state |
| Class metadata   | Runtime information about loaded classes     |
| Threads          | Native stacks and thread metadata            |
| Direct buffers   | Native payloads reached through Java objects |
| File mappings    | Resident pages from mapped files             |
| Native libraries | Allocations made outside the JVM             |

Three measurements describe different states:

- **Reserved memory** is virtual address space set aside for possible use.
- **Committed memory** has backing that the JVM can use.
- **Resident Set Size (RSS)** counts process pages currently in physical
  memory according to the operating system.

The HotSpot JVM implementation exposes reserved and committed runtime memory
through **Native Memory Tracking (NMT)**. RSS reports resident pages from the
heap, native allocations, shared libraries, and file mappings. Committed
memory need not be resident, so subtracting NMT totals from RSS does not
produce an exact accounting identity.

The measurements instead answer complementary questions:

```text
RSS grows
    -> the process has more resident pages

an NMT category grows during the same interval
    -> that JVM subsystem claims more memory

RSS grows while NMT stays stable
    -> inspect buffers, mappings, and native libraries
```

## Establish a synchronized baseline

NMT groups the JVM's native memory by runtime subsystem. It must begin
collecting at startup:

```text
-XX:NativeMemoryTracking=summary
```

Use `jcmd`, a diagnostic utility included with the **Java Development Kit
(JDK)**, to read the data. Replace `<pid>` with the operating-system process
identifier of the running JVM:

```bash
jcmd <pid> VM.native_memory summary scale=MB
```

NMT does not fully track native-library allocations, some JDK library
allocations, or file-backed mappings.

Take a baseline after startup and warmup:

```bash
jcmd <pid> VM.native_memory baseline
```

Run the representative workload for the observation interval, then request
the change since that baseline:

```bash
jcmd <pid> VM.native_memory summary.diff scale=MB
```

Record RSS over the same interval. A stable category does not explain new
growth; a smaller category that rises with RSS may.

## Follow growth in the Thread category

A **platform thread** uses an operating-system thread and a native stack for
method calls and local state. NMT's Thread category usually grows as the JVM
creates platform threads.

The rough capacity relationship is:

```text
stack reservation ~= platform-thread count * effective stack size
```

The `-Xss` option controls the requested stack size, but its default depends
on the platform. Inspect the effective JVM flags and the current threads:

```bash
jcmd <pid> VM.flags -all
jcmd <pid> Thread.print > threads.txt
```

Find `ThreadStackSize` in the flag output. Group the thread dump by name and
method-call path to find unbounded pools, per-request pools, or threads that
never terminate.

A stack reservation is not the same as resident memory. Pair rising thread
count and NMT Thread growth with rising RSS before attributing the physical
footprint to stacks.

## Follow growth in the Class category

**Metaspace** holds metadata for loaded Java classes. A **class loader**
defines classes and participates in their lifetime. If the application keeps
an old loader reachable after a reload, its classes and metadata can remain.

Inspect class-loader statistics with:

```bash
jcmd <pid> VM.classloader_stats
```

A large class count alone is not a leak because frameworks can legitimately
generate classes. The stronger pattern combines three growing signals:

```text
loaded classes
      +
class-loader count
      +
NMT Class memory
```

If old application loaders remain, inspect heap references to find what keeps
them reachable. `-XX:MaxMetaspaceSize` limits growth; it does not correct the
loader lifetime.

## Measure direct-buffer memory

A **direct byte buffer** keeps its payload in native memory. Its small
ByteBuffer heap object does not reveal the native payload's size.

The JVM management interface publishes buffer-pool estimates through a
**management bean**, a runtime metrics object queried by monitoring tools.
The direct-buffer pool uses this object name:

```text
java.nio:type=BufferPool,name=direct
```

Record its buffer count, total capacity, and memory used. Memory used can
differ from total capacity because of alignment and allocator details. Treat
both values as estimates and correlate their growth with RSS.

`-XX:MaxDirectMemorySize` limits direct-buffer allocations governed by the
`java.nio` mechanism. It does not limit memory requested independently by a
native library.

A pooled allocator may keep native regions for reuse. Compare its pool metrics
and capacity with RSS before treating retained memory as unbounded growth.

## Inspect resident file mappings

A **memory-mapped file** places file pages in the process address space. Pages
loaded into physical memory raise RSS without becoming Java heap objects.

On Linux, inspect the aggregate and individual mappings:

```bash
cat /proc/<pid>/smaps_rollup
less /proc/<pid>/smaps
```

`smaps_rollup` totals the process mappings. `smaps` shows each region and its
backing file. Focus on the `Rss` and `Pss` fields, not only the virtual `Size`.

RSS counts a shared resident page in every process that maps it.
**Proportional Set Size (PSS)** divides that page among those processes. PSS
therefore gives a more useful ownership estimate for shared libraries and
shared file mappings.

Storage libraries and `FileChannel.map()` commonly create large virtual
mappings. They consume physical memory only as their pages become resident.

## Profile growth outside the JVM ledgers

Another accounting gap appears when Java delegates work to native libraries
through the **Java Native Interface (JNI)**. That work can use a **native
allocator** to obtain and reuse memory outside the heap. NMT does not record
the library's request, and the heap may show only a small wrapper that points
to a much larger native allocation.

When RSS grows while the other measurements stay stable, use async-profiler,
a native and Java profiler, to record allocator activity:

```bash
asprof -e nativemem -d 300 -f native-memory.jfr <pid>
```

The `nativemem` event records allocation and release calls with their
method-call paths, or **stack traces**. Use async-profiler's `jfrconv` utility
to report allocations that have no matching release during the recording
window:

```bash
jfrconv --total --nativemem --leak \
  native-memory.jfr native-memory-leaks.html
```

An outstanding allocation is evidence, not proof of a leak. Allocators can
retain memory for reuse. Test profiling overhead and compare recordings under
the same workload.

If the process can restart with an instrumented allocator such as jemalloc,
it can provide a longer-running profile. It can also expose **allocator
fragmentation**: resident pages that the allocator cannot return or reuse
efficiently. Fragmentation can keep RSS high after live allocations shrink.

## Reconcile growth over one interval

The diagnosis comes from time-aligned measurements:

| Signal that grows with RSS | Likely contributor          |
|----------------------------|-----------------------------|
| Post-GC heap               | Retained Java objects       |
| NMT Thread                 | Platform threads and stacks |
| NMT Class                  | Classes and class loaders   |
| Direct-buffer memory       | Native buffer payloads      |
| Mapping RSS or PSS         | Resident mapped pages       |
| Native allocation profile  | Native library allocations  |

More than one row may grow. Explain the largest contributors first, then
profile the difference that remains. If nothing correlates with RSS, verify
that every measurement covers the same process, workload, and time interval.

Off-heap diagnostics succeeds when a large process becomes a small set of
measured contributors with explicit owners.

---

Return to [Troubleshooting](_index.md)
