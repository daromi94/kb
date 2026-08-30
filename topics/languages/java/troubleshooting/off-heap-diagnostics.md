# Off-heap diagnostics

A Java process can consume more physical memory than its Java heap. When
process memory rises while the heap remains stable, compare measurements from
the same interval until one non-heap component explains the growth.

> **Measure physical memory from outside the process, classify JVM-owned
> memory from inside it, and profile only the growth neither view explains.**

## Start at the process boundary

The Java Virtual Machine (JVM) runs inside an operating-system process. Its
Java heap stores application objects. Garbage collection (GC) can reclaim an
unreachable heap object, but the process also contains unmanaged regions:

| Process region   | What consumes memory                         |
|------------------|----------------------------------------------|
| Java heap        | Ordinary Java objects                        |
| Class metadata   | Runtime information about loaded classes     |
| Thread stacks    | Method calls and local state for each thread |
| Direct buffers   | Native payloads reached through Java objects |
| File mappings    | Resident pages from mapped files             |
| JVM runtime      | Collector, compiler, and compiled code       |
| Native libraries | Allocations made outside the JVM             |

Together, the process regions outside the Java heap form **off-heap memory**.
This is a diagnostic boundary, not one allocator or memory pool.

Suppose an order service shows this trend under steady traffic:

```text
process RSS:      3.2 GB -> 4.1 GB -> 5.5 GB
post-GC heap:     0.9 GB -> 0.9 GB -> 0.94 GB
```

**Resident Set Size (RSS)** counts process pages currently held in physical
memory. The stable post-GC heap cannot explain the additional 2.3 GB of RSS,
so a heap dump is not the first diagnostic artifact.

## Keep address space, commitment, and residency separate

A JVM can reserve virtual address space, make part of it available, and touch
only some of those pages:

```text
reserved     8.0 GB   virtual address range set aside
committed    3.0 GB   capacity available to the JVM
resident     2.1 GB   pages currently in physical memory
```

Reserved and committed values describe JVM capacity; RSS describes physical
residency. A committed page need not be resident, so compare changes instead
of subtracting JVM commitments from RSS.

## Establish one observation interval

On HotSpot, the JVM used by OpenJDK, **Native Memory Tracking (NMT)** groups
internal memory by subsystem. NMT is disabled by default and cannot start
after process launch. Choose its tracking level at startup:

```text
-XX:NativeMemoryTracking=summary
-XX:NativeMemoryTracking=detail
```

`summary` groups memory by subsystem. `detail` also records allocation call
sites. NMT can add roughly 5-10% performance overhead, so test the chosen
level before production use.

The Java Development Kit (JDK) includes `jcmd`, which queries a running JVM.
Replace `<pid>` with its process identifier. After warmup, set a baseline:

```bash
jcmd <pid> VM.native_memory baseline
```

Run the representative workload, then request the change:

```bash
jcmd <pid> VM.native_memory summary.diff scale=MB
```

Record RSS, post-GC heap, workload, and subsystem metrics over the same
interval. NMT tracks HotSpot internals, not third-party native code or JDK
class-library allocations. It is a classifier, not a complete process ledger.

## Let the changing signal choose the next question

Each signal points to a different owner:

| Signal that grows with RSS | Next question                               |
|----------------------------|---------------------------------------------|
| Post-GC heap               | Which Java objects remain reachable?        |
| NMT Thread                 | Why are platform threads or stacks growing? |
| NMT Class                  | Why do classes or class loaders remain?     |
| Direct-buffer capacity     | Which component owns the buffers or pool?   |
| Mapping residency          | Which mapped files became resident?         |
| Native allocation profile  | Which library allocation path remains?      |

Explain the largest measured contributors first, then investigate what
remains.

## Follow JVM-owned categories

A **platform thread** uses an operating-system thread and reserves native
stack space. If NMT Thread grows, compare it with the platform-thread count:

```text
stack reservation ~= platform-thread count * effective stack size
```

The `-Xss` option controls the requested stack size; its default depends on
the platform. Inspect the effective flags and current threads:

```bash
jcmd <pid> VM.flags -all
jcmd <pid> Thread.print > threads.txt
```

Find `ThreadStackSize`, then group the dump by thread name and call path. A
growing pool can explain the change. Require corresponding RSS growth because
reservation is not residency.

NMT Class grows with metadata stored in **metaspace**. Each class belongs to a
class loader. If an old loader remains reachable after an application reload,
its classes and metadata remain as well.

```bash
jcmd <pid> VM.classloader_stats
```

Look for class count, loader count, and NMT Class memory growing together. A
metaspace limit does not correct an unintended loader lifetime.

## Measure direct-buffer capacity separately

A direct byte buffer stores its payload outside the Java heap. Its ByteBuffer
wrapper remains in the heap, but the wrapper's heap bytes exclude the payload.

The BufferPoolMXBean management interface exposes estimates for this pool:

```text
java.nio:type=BufferPool,name=direct
```

Record buffer count, capacity, and memory used. The last two can differ
because of alignment and allocator details. Correlate both with RSS.

For the order service, the complete interval now looks like:

```text
process RSS change                 +2,300 MB
post-GC heap change                   +40 MB
NMT subsystem changes                 +90 MB
direct-buffer capacity change      +2,050 MB
```

Direct buffers are the strongest lead because capacity grew at the same time
and scale as RSS. Inspect the owning pool and its capacity policy.

`-XX:MaxDirectMemorySize` limits `java.nio` direct-buffer allocations, not
memory requested independently by a native library. A pool can also retain
regions for reuse, so retained capacity is not automatically a leak.

## Inspect resident file mappings

A memory-mapped file places a file region in virtual address space. RSS rises
only as the mapping's pages become resident.

On Linux, inspect the aggregate process mappings first:

```bash
cat /proc/<pid>/smaps_rollup
```

The report separates virtual mapping size from resident ownership:

```text
Size    complete virtual range
Rss     pages currently resident
Pss     proportional share of resident pages
```

RSS counts a shared page in every process that maps it. **Proportional Set
Size (PSS)** divides that page among those processes. If mapping residency
grows, inspect `/proc/<pid>/smaps` for the responsible file or anonymous
region. `FileChannel.map()` can create mappings without adding heap objects.

## Profile what the JVM measurements cannot explain

The **Java Native Interface (JNI)** lets Java call native libraries. A library
can allocate memory while leaving only a small Java wrapper in the heap. NMT
does not record that third-party allocation path.

If RSS grows while heap, NMT, buffers, and mappings stay stable, use
async-profiler to record native allocation and release calls:

```bash
asprof -e nativemem -d 300 -f native-memory.jfr <pid>
```

Convert the recording into a report of sampled allocations without a matched
release:

```bash
jfrconv --total --nativemem --leak \
  native-memory.jfr native-memory-leaks.html
```

The converter excludes recent allocations to reduce end-of-recording bias.
An unmatched allocation may still be live or retained for reuse, so it is
evidence rather than proof. Test profiler overhead.

With allocator fragmentation, live allocations shrink while partially used
regions keep RSS high. Confirm it with allocator metrics and process maps.

## Verify the proposed owner

After bounding the order service's direct-buffer pool, repeat the same traffic
and observation interval:

| Measurement                   | Before    | After   |
|-------------------------------|-----------|---------|
| Throughput                    | 5,000/s   | 5,000/s |
| Process RSS change            | +2,300 MB | +140 MB |
| Direct-buffer capacity change | +2,050 MB | +60 MB  |
| Post-GC heap change           | +40 MB    | +35 MB  |

The matching reduction in buffer growth and RSS supports the explanation.
Stable throughput and heap show that the result did not come from less work
or from moving pressure into the Java heap.

Off-heap diagnosis succeeds when time-aligned measurements turn a large
process into a bounded component with an explicit owner.

---

Return to [Troubleshooting](_index.md)
