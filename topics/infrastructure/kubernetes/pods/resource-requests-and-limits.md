# Resource requests and limits

Every container can declare **requests** and **limits** for CPU and
memory. Requests are the floor: the scheduler guarantees at least
that much on the target node, and the kernel uses them to divide
resources when containers compete. Limits are the ceiling, but they
behave asymmetrically — exceeding a memory limit kills the process,
while exceeding a CPU limit only throttles it.

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## CPU

CPU is measured in millicores. `1000m` equals one full core, `500m`
half a core.

- **Requests** set CPU shares in the underlying cgroup. When multiple
  containers contend for a core, each gets time in proportion to its
  shares. Shares of 1024 / 2048 / 3072 split as 16.7% / 33.3% / 50%.
- **Limits** set a time quota — CPU-seconds per wall-clock second. A
  limit of `1` means the process may use one CPU-second per second.
  Eight threads burn that in an eighth of a second and then wait
  (throttled) for the next period.

Exceeding a CPU limit throttles the process — it is never killed
for going over.

## Memory

Memory is measured in bytes. Kubernetes accepts SI suffixes
(`K`, `M`, `G`, `T`) or binary suffixes (`Ki`, `Mi`, `Gi`, `Ti`);
binary suffixes are preferred for hardware capacities.

Memory limits are **hard**. There is no time-slicing analog for
memory — a process either has the page or it does not. When usage
exceeds the limit, the kernel kills the process and Kubernetes marks
the container `OOMKilled`.

## Scheduling uses requests only

The scheduler looks at requests, never limits. It sums each Pod's
requests, then picks a node with enough unreserved capacity. Picture
it as Tetris: each Pod is a block sized by its requests, and the
scheduler packs blocks onto nodes.

A Pod with no requests has no block size. The scheduler will happily
stack unlimited such Pods on a node, which then collapses when real
usage spikes.

## The container-visibility gotcha

Setting limits does not change what the container sees. Inside the
container, `nproc`, `/proc/meminfo`, and the kernel still expose the
full node's CPU count and memory. Runtimes that auto-size from those
numbers will misconfigure themselves:

- JVM heap sized from host memory is a classic source of OOMKills
- Thread pools sized from `nproc` exceed the CPU limit and cause
  constant throttling
- Go's `GOMAXPROCS` defaults to `runtime.NumCPU()`, not the CPU limit

Applications have to be told their limits explicitly, or use
cgroup-aware helpers (JVM `UseContainerSupport`, Uber `automaxprocs`
for Go).

---

Return to [Pods](_index.md)
