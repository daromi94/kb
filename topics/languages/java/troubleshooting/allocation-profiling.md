# Allocation profiling

When the problem is allocation rate rather than retention, the GC runs
constantly because the app churns garbage. Heap-after-GC is modest but
GC is always working. A heap dump will not help here — it shows what
is retained, not what is being created and discarded.

## Recognizing the symptom

If Old Gen stays near 100% with Full GCs running back-to-back
reclaiming nothing, the issue is retention — use a heap dump. But if
heap-after-GC is modest and GC still runs constantly, the app is
allocating aggressively. The symptom looks like high memory use
because GC is always working, but the fix is fewer allocations on the
hot path, not more memory.

Watch GC behavior live:

```bash
jstat -gcutil <pid> 1000
```

## async-profiler

async-profiler in allocation mode produces a flame graph of allocation
sites weighted by bytes:

```bash
./profiler.sh -e alloc -d 60 -f alloc.html <pid>
```

This directly shows the hot path — the code allocating gigabytes per
second of temporary `byte[]` or boxed primitives.

## JDK Flight Recorder

JFR gives allocation data with lower overhead and is always available:

```bash
jcmd <pid> JFR.start duration=120s filename=rec.jfr settings=profile
```

Open in JDK Mission Control. The TLAB allocation view shows allocation
sites and rates. The GC view shows pause times and frequencies. If you
see 2GB/sec of allocation but 500MB steady-state heap, the answer is
allocation pressure.

JFR in continuous recording mode is the best default when the symptom
is unclear — it captures allocation, GC, locks, and I/O in one pass.

## GC log analysis

GC logs are essentially free and invaluable after the fact:

```text
-Xlog:gc*:file=gc.log:time,uptime:filecount=10,filesize=100M
```

Look for frequent Full GC events with little memory recovered.
Frequent Young GCs with large promotion rates indicate that
short-lived objects are surviving long enough to reach Old Gen,
often because allocation rate exceeds Young Gen capacity.

Export GC pause times and frequency via JMX or Micrometer. Sustained
high heap utilization after a GC cycle completes is the earliest
indicator of a problem — alert on post-GC occupancy, not raw heap
usage.

## Related

- [Symptom triage](symptom-triage.md) - Classifying the problem first
- [Heap dump analysis](heap-dump-analysis.md) - When retention is the issue
- [Memory accounting](memory-accounting.md) - Building a memory budget

---

Return to [Troubleshooting](_index.md)
