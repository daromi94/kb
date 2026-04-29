# CPU-bound databases

The classical picture of a database — CPU idle, waiting on disk — no longer
holds. When data sits in memory and storage is fast, the CPU becomes the
bottleneck.

## The shift

Spinning disks were once the slowest part of a server. The CPU spent most
of its time in I/O wait. High database latency meant slow disks.

Two changes broke that:

- **Buffer pools.** Engines cache hot pages in memory. A query served from
  cache is a logical read — RAM, not disk.
- **NVMe and SSDs.** Even on a cache miss, the disk delivers data fast
  enough to keep the CPU saturated.

Either way — cache hit or disk read — the CPU is no longer waiting. The
bottleneck is the computation itself: parsing SQL, searching the plan
space, sorting and hashing, scanning rows in memory, checking MVCC
visibility, contending on latches.

## What this means

A database pinned at 100% CPU is rarely a hardware sizing problem. It
signals that the workload — query shape, plan choices, concurrency — is
hitting the engine's expensive operations. Disk graphs can look calm while
the CPU pegs.

## Related

- [Overview](overview.md) — Database vs DBMS, why not flat files
- [Diagnosing CPU spikes](diagnosing-cpu-spikes.md) — Workload causes of high CPU

---

Return to [Databases](_index.md)
