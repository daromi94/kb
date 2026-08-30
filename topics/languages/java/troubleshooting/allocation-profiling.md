# Allocation profiling

The **Java Virtual Machine (JVM)** stores application objects in a memory area
called the **heap**. Creating an object reserves heap space; this operation is
an **allocation**. The amount of space reserved per unit of time is the
**allocation rate**.

When the application can no longer reach an object, **garbage collection
(GC)** can reclaim its space. Most objects may disappear quickly, yet creating
and reclaiming them is not free. At a high enough allocation rate, that work
can consume processor time, introduce pauses, and slow requests even while
the heap holds a moderate amount of data.

Allocation profiling finds the code paths responsible for that work.

## Retention and churn produce different shapes

Objects that remain reachable are **retained**. Together, the reachable
objects left after a collection form the **live set**. A growing live set is a
retention problem.

When the application instead creates short-lived objects at a high rate, GC
repeatedly reclaims them. This cycle is **allocation churn**: a large volume
of data moves through the heap, but the live set stays moderate.

The central distinction is:

> **Retention measures what remains. Allocation rate measures how quickly new
> objects enter the heap.**

```text
retention problem

post-GC heap:  1.0 GB -> 1.4 GB -> 1.9 GB -> 2.5 GB


allocation-churn problem

post-GC heap:  1.0 GB -> 1.1 GB -> 1.0 GB -> 1.1 GB
allocated:      40 GB     42 GB     39 GB     41 GB
```

This difference determines which diagnostic artifact is useful. A heap dump
captures the objects and references that still exist at one moment, so it can
explain retention. Short-lived objects usually disappear before the capture;
an allocation profile records their creation sites instead.

## Confirm that collection is doing useful work

Start with GC evidence before profiling code. A GC log records heap occupancy,
collection timing, and the space reclaimed by each collection.

The useful comparison is:

```text
heap before GC - heap after GC = memory reclaimed
```

Two patterns point in different directions:

| Observation                              | Interpretation      |
|------------------------------------------|---------------------|
| GC reclaims little; post-GC heap rises   | Retention pressure  |
| GC reclaims much; post-GC heap is stable | Allocation pressure |

High GC frequency alone is not enough. A collector can run frequently with
small, inexpensive collections. Measure the processor time, pause time, and
request latency associated with those collections.

If the service allocates 2 GB each second but retains only 500 MB after
collection, increasing the maximum heap may increase the time between
collections. It does not remove the work required to allocate and reclaim
those objects.

## Use Flight Recorder for a broad view

**Java Flight Recorder (JFR)** places runtime and application events on one
timeline. Each sampled allocation can include the method-call path that
created the object. That path is its **stack trace**. Because the recording
also contains GC, processor, lock, and input/output events, it can connect an
allocation burst to its source and its effect on the application.

Start a two-minute recording with `jcmd`, a diagnostic utility included with
the **Java Development Kit (JDK)**. Replace `<pid>` with the operating system
process identifier for the running JVM:

```bash
jcmd <pid> JFR.start \
  name=allocation-check \
  settings=profile \
  duration=120s \
  filename=/var/recordings/allocation-check.jfr
```

Open the recording in **JDK Mission Control (JMC)**. Its allocation views group
sampled events by class, thread, and stack trace. They also distinguish
allocations made inside and outside **Thread-Local Allocation Buffers
(TLABs)**. A TLAB gives one thread a small private heap region, allowing it to
allocate without contending with other threads. An object that does not fit
may be allocated outside the TLAB, but it still occupies the Java heap.

Use the recording to answer:

```text
Which classes account for the most allocated bytes?

Which threads create them?

Which stack traces lead to those allocation sites?

Do allocation bursts align with GC or latency spikes?
```

Recording every allocation would add substantial overhead, so JFR may
**sample** them by recording a representative subset. It may also aggregate
multiple events into totals. Treat its results as estimates that identify
dominant paths, not as an exact invoice for every object.

## Use async-profiler for an allocation flame graph

**async-profiler** can turn sampled allocation stacks into a **flame graph**.
This view combines related call paths and uses frame width to represent their
share of the sampled allocated bytes:

```bash
asprof -e alloc -d 60 -f allocation.html <pid>
```

A flame graph aggregates related stack traces:

```text
wide frame   = large share of sampled allocation
tall stack   = deeper call path
top frame    = method where allocation occurs
lower frames = callers that led there
```

The widest frame is not automatically defective. A request-decoding method may
allocate heavily because every request legitimately passes through it. The
actionable path combines high allocation volume with an avoidable design
choice. For example:

```text
handleOrder
   -> decodeRequest
      -> copyPayload
         -> new byte[requestSize]
```

If `copyPayload` duplicates an immutable request body that the decoder can
read directly, the stack exposes a removable copy. If the buffer must outlive
the request input, the allocation may be necessary.

## Look for mechanisms, not class names

Allocation pressure commonly comes from a small set of mechanisms:

| Mechanism             | Evidence in the profile                       |
|-----------------------|-----------------------------------------------|
| Repeated copying      | Large arrays allocated along conversion paths |
| Temporary collections | Lists and maps built only to traverse once    |
| Boxing                | Primitive values wrapped as objects in loops  |
| Parsing               | Decoding creates strings, tokens, and buffers |
| Logging               | Message construction on disabled paths        |
| Retry amplification   | Retries recreate the same request objects     |

The class name tells you what was allocated. The full stack tells you which
operation caused the allocation and whether that operation can change.

## Optimize only after connecting cost to impact

Prioritize a path when all three statements hold:

1. It contributes materially to the measured allocation rate.
2. Its allocations contribute to GC processor time, pauses, or request latency.
3. The code can remove, reuse, batch, or delay the objects without breaking
   ownership or correctness.

Typical changes include eliminating copies, reusing bounded buffers, parsing
only required fields, and avoiding intermediate collections. Object pooling
replaces repeated allocation with reuse, but it also makes object lifetimes
and concurrent access harder to manage. Use it only when measurement shows
that reuse improves the target workload.

## Verify the change with the same workload

Repeat the recording under comparable traffic after the change. Compare:

```text
allocation rate
GC processor time
GC pause time
request latency
post-GC live set
```

A successful change lowers allocation-related cost without increasing the
live set or moving pressure into **native memory**, the process memory outside
the Java heap.

Use a heap dump to explain what survives. Use an allocation profile to explain
what the application keeps creating.

---

Return to [Troubleshooting](_index.md)
