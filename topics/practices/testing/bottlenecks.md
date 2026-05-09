# Bottlenecks

Every system has exactly one bottleneck at any given moment — the
resource that saturates first as load increases. Relieve it and the
bottleneck moves; it never disappears. Performance work is iterative:
fix the database and the app server's CPU becomes the problem; fix
that and the network egress or a downstream API does. Capacity is set
by the most constrained resource, the way a chain's strength is set
by its weakest link.

Bottlenecks shift with workload shape. A read-heavy workload may be
limited by cache hit rate and database replicas; the same system
under writes may be limited by primary disk I/O or replication lag.
Test the wrong mix and you optimize for the wrong constraint.

## Common classes

**CPU.** Utilization climbs toward 100%, latency rises, throughput
plateaus. The trap on multi-core boxes: "100% CPU" can mean one core
pegged (serialization, hot lock, single-threaded code) or every core
evenly loaded (genuinely CPU-bound). The fixes are different. On
virtualized infrastructure also watch for CPU steal — the VM can be
starved by noisy neighbors even when its own utilization looks low.

**Memory.** Memory pressure rarely surfaces as out-of-memory first.
Symptoms come from garbage collection, swap activity, or page cache
eviction forcing disk I/O to spike. A JVM service under pressure
shows periodic latency spikes from GC pauses long before any OOM.
Memory leaks only surface under sustained load — a service that
looks fine for an hour can fall over at hour six.

**Disk I/O.** What matters is not just throughput in MB/s but IOPS,
queue depth, and latency per operation. A database doing many small
random writes can saturate the IOPS budget while using a fraction of
the bandwidth. Cloud block storage burst credits hide the limit
until they run out.

**Network.** Bandwidth, packet rate, or connection establishment.
The last bites hardest: a service that handles 10K req/s over
keep-alive can collapse at 1K req/s if every request opens a new
TLS connection. Handshakes are expensive and ephemeral port
exhaustion is real.

**Connection and thread pools.** The most common application-level
bottleneck and the most misdiagnosed. A pool sized at 20 caps
concurrency at 20 no matter how much headroom the downstream has.
Requests queue waiting for a slot, latency climbs, and from the
outside it looks like the database is slow — but the database is
bored. Same story with HTTP client pools and worker counts in
process-based servers.

**Locks and contention.** A hot row, a mutex around a shared
counter, a synchronized block — all serialize work that looks
parallel from the outside. The signature is that adding load does
not raise throughput, only latency, because workers wait for the
same lock. Amdahl's Law made visible: the serial fraction caps how
much parallelism can help.

**Downstream dependencies.** A service's capacity is bounded by the
slowest thing it calls. When that thing slows, the failure mode is
rarely graceful — cascading timeouts and retry storms start here.

---

Return to [Testing](_index.md)
