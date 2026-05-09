# Off-heap diagnostics

When NMT shows heap is fine but RSS is large, the problem is outside
the Java heap. NMT categories point the way.

## NMT workflow

NMT requires `-XX:NativeMemoryTracking=summary` at JVM startup. Once
enabled:

```bash
jcmd <pid> VM.native_memory summary
```

NMT breaks committed memory into Java Heap, Class (Metaspace),
Thread, Code (CodeCache), GC structures, Internal, Symbol, and
Other. Compare NMT's total against RSS — the delta is mapped files
and JNI allocations.

For tracking changes over time, set a baseline and diff:

```bash
jcmd <pid> VM.native_memory baseline
# ... wait ...
jcmd <pid> VM.native_memory summary.diff
```

## Thread stacks

Each thread reserves stack space (default 1MB, set by `-Xss`). A
2000-thread app with default stacks reserves 2GB just for stacks.
Thread pools with unbounded or misconfigured max sizes are the usual
cause.

Check thread count:

```bash
jcmd <pid> Thread.print | grep -c '^"'
```

## Metaspace

Dynamic class generation grows Metaspace. Check loaded class count:

```bash
jcmd <pid> VM.classloader_stats
```

Frameworks like Spring (proxies), Hibernate (entity enhancement),
Groovy, Kotlin reflection, and bytecode-manipulation libraries all
generate classes at runtime. A healthy app loads 10-30k classes;
100k+ suggests a classloader leak or runaway proxy generation.

Cap with `-XX:MaxMetaspaceSize`.

## Direct ByteBuffers

NMT's Internal/Other category often includes direct buffer
allocations. Check the JMX bean for precise accounting:

```text
java.nio:type=BufferPool,name=direct
```

This reports count and total capacity of direct buffers. Cap with
`-XX:MaxDirectMemorySize`.

For Netty applications, the pooled allocator sizes arenas per-thread
(`io.netty.allocator.numDirectArenas` multiplied by chunk size,
default 16MB chunks). A Netty app with many event loop threads can
commit hundreds of MB of direct memory by design before any traffic.
Tune `numDirectArenas` and `maxOrder` if disproportionate to
throughput needs.

## Memory-mapped files

Mapped files show up in RSS but not in NMT or direct buffer pools.
Check `/proc/<pid>/smaps` and look for large mappings. Lucene,
RocksDB, Chronicle, and anything using `FileChannel.map()` lives
here.

## JNI and native library allocations

Pure JNI `malloc` calls from native libraries are invisible to NMT.
If NMT's total is far below RSS and mapped files are ruled out, a
native library is allocating via `malloc`.

Diagnose with jemalloc profiling:

```bash
LD_PRELOAD=libjemalloc.so \
MALLOC_CONF=prof:true,lg_prof_interval:30 \
java ...
```

Analyze dumps with `jeprof`. This is the only reliable way to
attribute native allocations to call sites. async-profiler with
`--nativemem` mode is an alternative that can profile native memory
allocations without replacing the system allocator.

---

Return to [Troubleshooting](_index.md)
