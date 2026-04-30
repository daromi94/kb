# Tail-targeted engineering

At hyperscale, the mean is the wrong target. User-visible latency
lives in the tail, and narrowing it takes different techniques.

## The toolkit

**Hedged requests.** Issue the request to two replicas, take the
first response, cancel the other. If the tails are independent, a
1% tail on either replica becomes a 0.01% tail on the pair. Tied
variants — replicas that signal each other the moment one begins
executing — cancel the loser before it runs, keeping the extra load
small.

**Deadline propagation.** Every inbound request carries a deadline
that each layer of the call tree passes down. Downstream services
abandon work that will miss it, so a slow leaf cannot block the
tree on output no one will read.

**GC-aware routing.** Drain a node before a scheduled stop-the-world
pause and restore it after. The pause still happens — just not
while serving user traffic.

**CPU pinning and NUMA-aware scheduling.** Pin threads to cores and
allocate memory on the local NUMA node. Scheduler migration and
remote-memory access are pure variance: the mean barely moves, the
tail shrinks.

**Off-heap or arena allocation.** Keep high-churn buffers off the
managed heap. A smaller heap means shorter GC pauses and a narrower
tail.

**Low-overhead I/O paths.** A syscall-heavy I/O path has a tail
dominated by scheduler decisions, not by the device. io_uring
amortizes syscall cost via shared rings; DPDK and AF_XDP move
packet handling to userspace entirely. Both shrink or remove the
kernel's contribution to latency.

## The common thread

Each technique narrows a distribution rather than lowering its mean.
Variance is the adversary.

## Related

- [Fanout tail amplification](fanout-tail-amplification.md) - Why tails dominate user latency
- [Rarity as frequency](rarity-as-frequency.md) - Tail events at scale

---

Return to [Latency](_index.md)
