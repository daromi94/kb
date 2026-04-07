# ByteBuf allocators

Allocating a direct buffer is roughly two orders of magnitude slower
than a heap buffer. Netty's pooled allocator amortizes that cost
through arena-based memory management and thread-local caching.

## Allocator strategies

Netty ships two allocators:

- **PooledByteBufAllocator** — the default. Reuses memory through
  arenas and thread-local caches.
- **UnpooledByteBufAllocator** — every allocation is a fresh `byte[]`
  or native block, freed on `release()`. Simpler, but every direct
  allocation pays the full syscall cost.

## Pooled allocator architecture

PooledByteBufAllocator uses a jemalloc-derived design. Memory is
organized hierarchically:

```text
Arena
  └── Chunk (4 MiB default = pageSize << maxOrder)
        └── Page (8 KiB default)
              └── Subpage (for small allocations)
```

Allocations fall into size classes:

| Class  | Range               | Served from              |
|--------|---------------------|--------------------------|
| Small  | Up to one page      | Subpage slabs in a chunk |
| Normal | Up to chunk size    | Pages within a chunk     |
| Huge   | Larger than a chunk | Unpooled; bypasses pool  |

Huge allocations create a one-off unpooled chunk and destroy it on
release — they never enter the pool.

### Thread-local caching

Each FastThreadLocalThread gets a PoolThreadCache holding recently
released buffers by size class. A cache hit is lock-free. A miss falls
through to the arena under a ReentrantLock. Non-Netty threads do not
get a cache by default (`useCacheForAllThreads` is false).

### Tuning

Arena count defaults to `2 * availableProcessors`, capped so the pool
does not consume more than half of `-XX:MaxDirectMemorySize`.

| Property                               | Default   |
|----------------------------------------|-----------|
| `-Dio.netty.allocator.type`            | `pooled`  |
| `-Dio.netty.allocator.numDirectArenas` | 2 * cores |
| `-Dio.netty.allocator.numHeapArenas`   | 2 * cores |
| `-Dio.netty.allocator.pageSize`        | 8192      |

Tuning matters mainly when the event loop count is unusual or direct
memory is constrained.

## Related

- [ByteBuf](bytebuf.md) - Netty's buffer abstraction
- [Resource management](resource-management.md) - Buffer ownership and release
- [Leak detection](leak-detection.md) - Diagnosing unreleased buffers

---

Return to [Netty](_index.md)
