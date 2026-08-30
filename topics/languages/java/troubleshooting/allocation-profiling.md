# Allocation profiling

A stable heap does not mean that memory behavior is cheap. An application can
create gigabytes of short-lived objects, reclaim almost all of them, and still
lose processor time to garbage collection. Allocation profiling estimates
which code paths create those objects and connects that activity to its
performance cost.

> **A heap dump explains what survives. An allocation profile explains what
> the application keeps creating.**

## Two memory problems leave different evidence

The Java Virtual Machine (JVM) stores application objects in a memory region
called the **heap**. Creating an object reserves heap space; that operation is
an **allocation**. The number of bytes allocated per unit of time is the
**allocation rate**.

Garbage collection (GC) reclaims an object's space after the application can
no longer reach it. The reachable objects that remain after GC has evaluated
the relevant heap regions form the **live set**. Compare live-set estimates
only after collections with the same scope and under equivalent workloads.

Retention makes the live set grow. **Allocation churn** produces a different
shape: the application creates short-lived objects rapidly, GC reclaims them,
and the live set remains roughly stable.

```text
retention

post-GC heap:      1.0 GB -> 1.4 GB -> 1.9 GB -> 2.5 GB


allocation churn

post-GC heap:      1.0 GB -> 1.1 GB -> 1.0 GB -> 1.1 GB
allocation rate:   650 MB/s  680 MB/s  640 MB/s  670 MB/s
```

A heap dump captures an object graph at one moment, so it can explain why
objects remain reachable. Short-lived objects often disappear before that
capture. An allocation profile instead samples their creation and records the
method-call paths that produced them.

## Confirm allocation pressure before profiling code

Start with evidence that connects GC activity to application cost. GC logs or
Java Flight Recorder data can show heap occupancy, collection frequency,
processor time, pause time, and request latency on one timeline.

For equivalent collection scopes, compare the heap before and after each
collection. A large reduction means that the collection reclaimed many
bytes; the difference is a useful estimate rather than an exact accounting
identity, especially when collection and application work overlap.

| Observation                              | Likely direction    |
|------------------------------------------|---------------------|
| Little reclaimed; post-GC heap rises     | Retention pressure  |
| Much reclaimed; post-GC heap stays level | Allocation pressure |

High collection frequency alone does not prove a problem. Collections may be
frequent and inexpensive. Profile allocations when GC processor time, pauses,
or request latency materially harms the workload while the post-GC heap stays
bounded.

Suppose a service allocates 650 MB each second but retains only 500 MB after
comparable collections. A larger maximum heap may delay some collections,
but it does not remove the work that creates and eventually reclaims those
temporary objects.

## Record a representative interval

Java Flight Recorder (JFR) records JVM and application events on a shared
timeline. Its allocation samples include the object class, thread, and stack
trace. A **stack trace** is the active chain of method calls that led to an
event.

Record a short interval after startup and workload warmup. The Java
Development Kit (JDK) provides `jcmd`, which sends diagnostic commands to a
running JVM. Replace `<pid>` with the operating-system process identifier:

```bash
jcmd <pid> JFR.start \
  name=allocation-check \
  settings=profile \
  duration=120s \
  filename=/var/recordings/allocation-check.jfr
```

Open the recording in JDK Mission Control (JMC). Group allocation samples by
class, thread, and stack trace, then compare bursts with GC activity and
request latency:

```text
Which classes account for the most allocated bytes?
Which threads create them?
Which call paths reach those allocation sites?
Do allocation bursts coincide with GC or latency spikes?
```

The profile configuration records a representative subset of allocations.
Each sample has a statistical weight that estimates how much allocation
pressure it represents. Aggregate those weights over many samples to find
dominant paths; do not treat the result as an exact invoice for every object.

Most allocations do not require threads to coordinate. HotSpot, the JVM
implementation used by OpenJDK, usually gives each thread a small private heap
region called a **Thread-Local Allocation Buffer (TLAB)**. Dedicated JFR
events can distinguish allocations inside and outside TLABs, but the command
above does not enable them by default. Its general allocation samples answer
the main question: which call paths create the heap pressure?

## Follow the allocation path visually

For a focused view of allocation paths on a HotSpot-based JVM, async-profiler
can produce an allocation **flame graph**. The graph combines sampled stack
traces into rectangles called frames:

```bash
asprof -e alloc -d 60 -f allocation.html <pid>
```

Frame width represents the path's share of estimated heap pressure. Vertical
position represents the call chain, not elapsed time. In async-profiler's
allocation view, the top frame names the allocated class. The method directly
below it is the allocation site, and lower frames are its callers.

```text
byte[]                 allocated class
copyPayload            allocation site
decodeRequest          caller
handleOrder            entry point
```

The widest path is not automatically defective. A decoder may allocate
heavily because every request passes through it. The actionable question is
whether the path combines high volume with an avoidable operation.

Suppose `copyPayload` duplicates an immutable request body before parsing it:

```text
handleOrder
    -> decodeRequest
        -> copyPayload
            -> new byte[requestSize]
```

If the parser can safely read the original body, the profile has exposed a
removable copy. If another component must own the bytes after the input is
released, the copy establishes a necessary lifetime boundary.

## Look for the mechanism behind the class

The allocated class describes what consumes heap space. The full call path
reveals the operation that creates it:

| Mechanism             | Evidence in the profile                        |
|-----------------------|------------------------------------------------|
| Repeated copying      | Large arrays below conversion or parsing paths |
| Temporary collections | Lists or maps built only for one traversal     |
| Boxing                | Primitive values repeatedly wrapped as objects |
| Parsing               | Strings and buffers created while decoding     |
| Eager logging         | Messages built before a discarded log event    |
| Retry amplification   | Each retry recreates the same request objects  |

Prioritize a path only when it materially contributes to allocation rate,
its GC cost harms the workload, and the code can change without violating
ownership or correctness.

Common corrections remove copies, parse only required fields, avoid
intermediate collections, or reuse a bounded buffer. Object pooling reuses
instances instead of repeatedly allocating them, but it complicates object
lifetime and concurrent access. Use pooling only when measurement shows that
reuse improves the target workload.

## Verify cost per unit of work

Repeat the same recording under comparable traffic after the change. Compare
both total rate and cost per completed request; lower traffic alone can make
an unchanged path appear cheaper.

| Measurement           | Before           | After            |
|-----------------------|------------------|------------------|
| Throughput            | 5,000 requests/s | 5,000 requests/s |
| Allocated per request | 96 KB            | 44 KB            |
| Allocation rate       | 480 MB/s         | 220 MB/s         |
| GC processor time     | 28%              | 13%              |
| Post-GC heap          | 510 MB           | 505 MB           |

This result supports the explanation: removing the payload copy reduced both
allocation per request and GC cost at the same throughput. The stable post-GC
heap also shows that the change did not trade churn for retention.

Check process memory as well. A direct buffer stores its payload outside the
Java heap. Replacing heap arrays with direct buffers can move pressure into
**native memory**, the rest of the process memory, rather than remove it.

Allocation profiling succeeds when it connects a costly allocation rate to a
specific call path, a removable mechanism, and a measured improvement under
the same workload.

---

Return to [Troubleshooting](_index.md)
