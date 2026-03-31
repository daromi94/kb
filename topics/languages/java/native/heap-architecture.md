# Heap architecture

The JVM heap is structured around the weak generational hypothesis: most
objects become unreachable shortly after allocation. The heap is split
into regions tuned for different object lifetimes.

## Young generation

All new objects start here. The region is optimized for rapid allocation
and frequent, low-latency collection.

**Eden space.** The initial allocation zone. Memory is assigned
sequentially via bump-the-pointer — advance a pointer by the object's
size and return the old pointer value. Each thread gets a Thread-Local
Allocation Buffer (TLAB) so allocation is lock-free.

**Survivor spaces (S0 and S1).** When Eden fills, a Minor GC copies
live objects into one empty Survivor space. On subsequent Minor GCs,
survivors are copied between S0 and S1 while an internal age counter
increments each cycle.

```text
+--------------------------------------+
| Young generation                     |
|                                      |
|  +--------+  +--------+  +--------+  |
|  | Eden   |  |   S0   |  |   S1   |  |
|  |        |  |        |  |        |  |
|  | TLAB.. |  | age 1  |  | age 2  |  |
|  +--------+  +--------+  +--------+  |
|      |           |            |      |
|      +-----------+------------+      |
|            Minor GC copies           |
+--------------------------------------+
```

## Old generation (tenured)

Objects surviving enough Minor GC cycles (the tenuring threshold) are
promoted here. This region is larger and holds long-lived data such as
connection pools, application state, and caches.

Collection of the old generation is more expensive. Traditional
collectors and Full GC fallbacks use stop-the-world pauses that halt
all application threads. Modern collectors (G1, ZGC, Shenandoah)
perform old-generation collection mostly concurrently, avoiding or
minimizing pauses under normal operation.

## Metaspace

Metaspace is structurally separate from the heap. It is allocated from
native OS memory (off-heap) and can grow dynamically.

| Stored in Metaspace                | Stored elsewhere              |
|------------------------------------|-------------------------------|
| Class metadata (Klass structures)  | Static field values → heap    |
| Method metadata and bytecode       | JIT-compiled code → CodeCache |
| Constant pools                     | Interned strings → heap       |
| Annotations and JIT profile counts |                               |

Static variables live on the Java heap, attached to the `java.lang.Class`
mirror object — not in Metaspace. JIT-compiled machine code occupies the
CodeCache, a separate native memory region sized by
`-XX:ReservedCodeCacheSize`.

## Related

- [Heap vs off-heap memory](heap-vs-off-heap.md) - GC-managed vs native
  memory and the native boundary problem

---

Return to [Native interop](_index.md)
