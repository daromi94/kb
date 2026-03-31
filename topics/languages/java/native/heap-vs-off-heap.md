# Heap vs off-heap memory

The JVM manages two fundamentally different memory regions, and
understanding the distinction is essential for native interoperability.

## Heap memory

The JVM heap is managed entirely by the garbage collector. When an
object is instantiated, the JVM allocates space within this region.
The GC tracks object reachability and automatically reclaims memory
when objects become unreachable.

Collectors like G1, ZGC, and Shenandoah compact the heap by moving
objects to new virtual addresses. This eliminates fragmentation but
means heap addresses are inherently unstable. A native C function
expects a fixed pointer — if the GC relocates the underlying object
mid-call, the result is memory corruption or a crash.

## Off-heap memory

Off-heap (native) memory is allocated outside the GC-managed heap,
in the process's virtual address space via the C library's `malloc`
(which internally uses `brk` or `mmap` depending on allocation
size). Once allocated, an off-heap region keeps its virtual address
until explicitly freed. The GC will never scan, compact, or
relocate off-heap contents.

Two properties make off-heap memory essential for performance and
native interop:

**Deterministic latency.** The GC does not scan off-heap memory for
reachability. Storing large datasets (gigabytes of cached data)
off-heap prevents GC pause times from growing with dataset size.

**Stable virtual addresses.** Off-heap memory is never relocated by
GC compaction. A native C function or OS kernel call can safely
receive a pointer to an off-heap region without risk of the address
becoming invalid mid-call.

The GC is not entirely uninvolved, though. A DirectByteBuffer has a
small on-heap wrapper with a Cleaner (PhantomReference). When the GC
collects that wrapper, the Cleaner deallocates the off-heap memory.
The JVM can also trigger GC when direct buffer allocation approaches
`-XX:MaxDirectMemorySize`.

```text
+--------------------------+     +-------------------------+
| JVM heap                 |     | Off-heap memory         |
|                          |     |                         |
| Objects allocated by new |     | Allocated via OS malloc |
| GC tracks reachability   |     | GC does not scan/move   |
| GC compacts — moves objs |     | Fixed virtual address   |
| Addresses are unstable   |     | Freed explicitly or by  |
|                          |     | Cleaner / Arena.close() |
+--------------------------+     +-------------------------+
```

## Related

- [Heap architecture](heap-architecture.md) - Generational heap layout

---

Return to [Native interop](_index.md)
