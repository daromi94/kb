# Memory hierarchy geometry

The memory hierarchy spans many orders of magnitude. An L1 hit is
a handful of CPU cycles; a DRAM miss stalls the core for hundreds;
a storage miss burns hundreds of thousands; a cross-datacenter
round-trip burns hundreds of millions. The core is doing nothing
useful for almost all of those cycles.

Each major tier boundary — cache to DRAM, DRAM to storage, local
to remote — is at least an order of magnitude, often more. The
tier the working set lives in is almost always the bottleneck, not
the CPU or the algorithm.

| Tier               | Typical latency |
|--------------------|-----------------|
| L1 cache           | ~1 ns           |
| L2 cache           | ~4 ns           |
| L3 cache           | ~10–20 ns       |
| Main memory (DRAM) | ~80–100 ns      |
| NVMe storage       | ~20–100 μs      |
| Rotational disk    | ~10 ms          |
| Cross-datacenter   | ~50–100 ms      |

## Location beats algorithm

A linear scan of cache-resident data beats a binary search that
misses into DRAM. An in-memory join beats a disk-spilling optimizer
regardless of asymptotic complexity. No micro-optimization closes a
tier-sized gap — only moving the data to a faster tier does.

Pick the tier first, then pick the algorithm.

## The same shape at every scale

The same tier-jump structure reappears one level up: CDN edge vs
origin, buffer pool vs disk, same-rack vs cross-region. A
cache-line–aware struct, a working-set-sized buffer pool, and a
regional replica are the same move at different scales — keep the
working set in the nearest tier that holds it.

## When you cannot keep data close

If a hot-path operation needs data from a slower tier, the two
options are: pull the data up (prefetch, cache, replicate) or push
the computation down (move the code to where the data already
lives). Everything else is rearranging deck chairs on the wrong
tier.

## Related

- [Latency constants](latency-constants.md) - Speed-of-light limits

---

Return to [Latency](_index.md)
