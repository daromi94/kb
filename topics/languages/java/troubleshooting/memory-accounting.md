# Memory accounting

When there is no OOM and no crash, the investigation is memory
accounting: building a budget that explains every megabyte. The
question is not "what's leaking" but "where is my memory going."

## Split the total

Compare RSS from the OS (`ps`, `top`, container metrics) against the
JVM's own view:

```bash
jcmd <pid> GC.heap_info
jcmd <pid> VM.native_memory summary
```

NMT requires `-XX:NativeMemoryTracking=summary` at JVM startup. The
output breaks committed memory into categories:

```text
Java Heap   (reserved=4GB,   committed=4GB)
Class       (reserved=1GB,   committed=256MB)
Thread      (reserved=512MB, committed=512MB)
Code        (reserved=256MB, committed=180MB)
GC          (reserved=400MB, committed=400MB)
Internal    (...)
```

Before touching a heap dump, you should be able to say: "RSS is 8GB,
of which heap accounts for 4GB, threads 500MB, Metaspace 256MB, GC
structures 400MB, direct buffers 2GB, unaccounted 800MB." That
sentence tells you where to dig. If heap is only 30% of RSS, profiling
the heap is a waste of time.

## Write a budget

The discipline that makes this investigation tractable:

```text
Expected:
  Heap (-Xmx):             4096 MB
  Metaspace cap:            512 MB
  Direct memory cap:        512 MB
  Thread stacks (200×1MB):  200 MB
  Code cache:               240 MB
  GC overhead (~10%):       400 MB
  ------
  Total expected:         ~5960 MB

Actual RSS:                8200 MB
Unexplained:               2240 MB
```

That unexplained delta is the investigation. If the numbers match, the
app is using exactly what it was configured to use — the question
becomes whether the caps are right for your workload.

The JVM is not frugal by default. It treats `-Xmx` as permission, not
a target. A huge fraction of "why does my Java app use so much memory"
turns out to be "because `-Xmx` is 8GB and the JVM happily grows to
fill it."

## Pragmatic investigation order

Stop as soon as the picture is clear:

1. **NMT summary + RSS comparison.** Resolves ~40% of cases by
   revealing the problem is threads, Metaspace, or direct buffers
   rather than heap.
2. **Class histogram.** Run `jcmd <pid> GC.class_histogram | head -30`
   for a fast, low-impact breakdown of instance counts and byte sizes
   without a full heap dump. Look for massive counts of custom classes
   or large `byte[]` / `char[]` arrays.
3. **Heap dump after forced Full GC.** If heap dominates, one dump
   opened in MAT, dominator tree top 20.
4. **NMT category drill-down.** If off-heap dominates, follow the
   category that stands out.
5. **jemalloc profiling.** If nothing adds up, native allocations.
6. **JFR.** If the issue is allocation rate rather than retention.

## Production readiness

Configure these flags proactively so diagnostic data is available when
failure occurs:

| Flag                               | Purpose                           |
|------------------------------------|-----------------------------------|
| `-XX:+HeapDumpOnOutOfMemoryError`  | Auto-capture dump at OOM          |
| `-XX:HeapDumpPath=/var/dumps`      | Dump location with disk space     |
| `-XX:NativeMemoryTracking=summary` | Enable NMT (5-10% overhead)       |
| `-Xms` = `-Xmx`                    | Lock heap size, prevent resizing  |
| `-XX:MaxMetaspaceSize=N`           | Cap Metaspace growth              |
| `-XX:+UseContainerSupport`         | Respect container memory limits   |
| `-XX:MaxRAMPercentage=N`           | Dynamic heap sizing in containers |

GC logging (essentially free, invaluable after the fact):

```text
-Xlog:gc*:file=gc.log:time,uptime:filecount=10,filesize=100M
```

Setting `-Xms` equal to `-Xmx` prevents latency spikes from the JVM
pausing to request or release memory to the OS.

In containers, `-XX:MaxRAMPercentage` is preferred over hardcoded
`-Xmx` values to allow dynamic sizing relative to the container limit.

## Related

- [Symptom triage](symptom-triage.md) - Classifying the problem first
- [Heap dump analysis](heap-dump-analysis.md) - MAT workflow and patterns
- [Off-heap diagnostics](off-heap-diagnostics.md) - Non-heap investigation

---

Return to [Troubleshooting](_index.md)
