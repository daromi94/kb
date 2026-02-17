# Leak detection

Netty's `ResourceLeakDetector` monitors pooled ByteBuf allocations to
catch buffers that are garbage-collected without being released. By
default, it samples roughly 1% of allocations, keeping overhead low while
still surfacing leaks as `LEAK` error log messages.

## Detection levels

Set the level with the JVM option `-Dio.netty.leakDetectionLevel=<LEVEL>`:

| Level      | Behavior                                           |
|------------|----------------------------------------------------|
| `DISABLED` | No detection; only for verified production systems |
| `SIMPLE`   | Default; reports leaks at ~1% sampling rate        |
| `ADVANCED` | Reports leaks with last-access location            |
| `PARANOID` | Samples every access; high overhead, debug only    |

`SIMPLE` catches most leaks in production. Switch to `ADVANCED` or
`PARANOID` when reproducing a specific leak in development — the
last-access trace pinpoints which handler failed to release.

## Related

- [Resource management](resource-management.md) - Ownership rules that
  prevent leaks
- [ByteBuf](bytebuf.md) - Buffer structure and reference counting

---

Return to [Netty](_index.md)
