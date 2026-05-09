# Heap dump analysis

When a memory leak is confirmed inside the heap or the dominator
breakdown is needed, a heap dump is the definitive diagnostic artifact.

## Capture

Force a GC first to see retained objects, not transient garbage:

```bash
jcmd <pid> GC.run
jcmd <pid> GC.heap_dump /tmp/heap.hprof
```

Dumps are roughly the size of used heap — ensure disk space. For
production, configure `-XX:+HeapDumpOnOutOfMemoryError` with
`-XX:HeapDumpPath` so a dump is captured automatically at the moment
of failure.

## Eclipse MAT workflow

Eclipse MAT is the standard tool for heap analysis. VisualVM works for
smaller dumps.

**Dominator Tree.** Start here, not the histogram. Shallow size lies —
a HashMap instance is tiny, but if it retains 2GB of entries, its
retained size is 2GB. Sort by retained size. The top 20 dominators
usually explain 80%+ of the heap.

**Retained size** answers: "if this object vanished, how much memory
would be freed?" This is the metric that matters.

**Leak Suspects Report.** MAT's automated first pass that identifies
objects holding the most retained memory. Good for orientation.

**Path to GC Roots.** Right-click a suspicious dominator, select
Path to GC Roots, exclude weak/soft references. This reveals *why*
the object is still alive: "because it's in this ConcurrentHashMap
field of this CacheManager." Common GC roots are static variables,
active threads, and ThreadLocal maps.

**Group by package.** On the histogram, group by package to see
whether the heap is dominated by `com.yourcompany.orders.*`,
`org.hibernate.*`, or `io.netty.*`. This reframes the problem
immediately.

## Common heap patterns

**Unbounded caches.** A ConcurrentHashMap retaining millions of
entries because nothing evicts. Look for `HashMap$Node[]` tables
dominating the heap. Check configured max size versus actual size for
Caffeine, Ehcache, Hibernate second-level cache, or Guava caches.

**Framework-internal caches.** Hibernate SessionFactory statistics,
Jackson TypeFactory, reflection caches, compiled regex patterns,
prepared statement caches. Legitimate but often oversized by default.

**ClassLoader leaks.** Multiple instances of the same class, or a
WebappClassLoader surviving redeploy. Common in app servers and
dynamic class generation.

**ThreadLocal leaks.** Values retained by long-lived thread pool
threads. The dominator path goes through Thread, ThreadLocalMap, then
your object. Call `remove()` on ThreadLocals in pooled-thread
environments.

**Listener/observer leaks.** Event sources holding references to
listeners that were never unregistered.

**Oversized collections from queries.** Loading an entire table into
memory instead of streaming.

**Static collections.** Anything held by a `class` root in MAT — enum
caches, singleton registries, logger contexts.

**String and byte arrays.** Usually a symptom, not a cause. Find their
dominator to identify who holds all those strings.

## Two-dump comparison for leaks

A single dump shows state. Two dumps taken an hour apart show growth.
In MAT, use the histogram comparison feature to see which classes
grew. Growth plus high retained size identifies the leak.

For ongoing detection, alert on heap-after-Full-GC climbing
monotonically over days — this is the unambiguous leak signature.
Monitor heap-after-GC (not raw heap usage), GC pause time and
frequency, and Old Gen occupancy.

---

Return to [Troubleshooting](_index.md)
