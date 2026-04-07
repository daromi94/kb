# Leak detection

Netty's ResourceLeakDetector monitors pooled ByteBuf allocations to
catch buffers that are garbage-collected without being released. By
default, it samples 1 in 128 allocations, keeping overhead low while
still surfacing leaks as `LEAK` error log messages.

## Detection levels

Set the level with the JVM option `-Dio.netty.leakDetection.level=<LEVEL>`:

| Level      | Sampling rate | Access traces | Behavior                                  |
|------------|---------------|---------------|-------------------------------------------|
| `DISABLED` | None          | No            | No detection; only for verified prod      |
| `SIMPLE`   | 1/128         | No            | Default; reports that a leak exists       |
| `ADVANCED` | 1/128         | Yes           | Reports leaks with recent access location |
| `PARANOID` | Every alloc   | Yes           | Tracks all allocations; debug only        |

`SIMPLE` catches most leaks in production. Switch to `ADVANCED` or
`PARANOID` when reproducing a specific leak in development — the
access traces pinpoint which handler failed to release.

## Related

- [Resource management](resource-management.md) - Ownership rules preventing leaks
- [ByteBuf](bytebuf.md) - Buffer structure and reference counting

---

Return to [Netty](_index.md)
