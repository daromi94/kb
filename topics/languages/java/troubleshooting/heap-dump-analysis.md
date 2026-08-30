# Heap dump analysis

A heap dump captures the Java heap as a graph of objects and references. The
largest object or most common class is rarely the whole diagnosis. The useful
question is why those objects are still reachable.

> **A large object is only a symptom until its reference path identifies the
> component that controls its lifetime.**

## Reachability turns the heap into an object graph

The Java heap stores application objects managed by garbage collection (GC).
GC begins with references that the Java Virtual Machine (JVM) always treats as
reachable. These **GC roots** include active thread stacks, static fields, and
references held by JVM runtime structures.

GC follows references outward from those roots. Anything it can reach must
remain in the heap. An object with no remaining path from a root is eligible
for collection.

```text
GC root: static field
          |
          v
     CacheRegistry
          |
          v
       OrderCache
          |
          +--> map entry --> OrderSummary
          +--> map entry --> OrderSummary
          +--> map entry --> OrderSummary
```

The **shallow size** of `OrderCache` is the space occupied by that object
alone. Its **retained set** contains the objects that would become collectible
if the cache became unreachable. Their combined shallow size is the cache's
**retained size**.

A cache object can be tiny while retaining gigabytes of map nodes, keys,
values, and byte arrays. Retained size shifts the investigation from storage
classes to lifetime owners.

## Choose the state before capturing it

A heap dump preserves one state of one JVM. Choose that state according to
the question being investigated:

| Capture point          | Question it helps answer                                |
|------------------------|---------------------------------------------------------|
| After allocation fails | What survived the JVM's attempts to recover space?      |
| During controlled load | What owns memory at a reproducible workload point?      |
| After expected cleanup | What remains after requests or jobs should be finished? |

The Java Development Kit (JDK) includes `jcmd`, a diagnostic utility that
sends commands to a running JVM. Here, `<pid>` means the operating-system
process identifier of the target JVM:

```bash
jcmd <pid> GC.heap_dump /var/dumps/orders-service-live.hprof
```

By default, this command requests a full GC and records reachable objects. The
result shows the surviving heap, but the collection may remove short-lived
objects that contributed to an allocation burst.

If the investigation needs the heap without that requested full collection,
use `-all`:

```bash
jcmd <pid> GC.heap_dump -all /var/dumps/orders-service-all.hprof
```

This form includes objects that are unreachable but not yet reclaimed. It
preserves more pre-collection state, but the dump is usually larger and
noisier because some recorded objects are already garbage.

Both forms are high-impact operations. A large dump can pause the JVM and
consume substantial disk space. Check the available space, use persistent
storage, and give each capture a distinct filename.

For Java heap exhaustion, the JVM can capture a dump automatically:

```text
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/dumps
```

The dump shows what survived the failed allocation and the JVM's recovery
attempts, not every transient object present when pressure began. These
options do not cover every `OutOfMemoryError`; failure to create a native
thread, for example, is not Java heap exhaustion.

## Build one ownership explanation

Eclipse Memory Analyzer (MAT) examines a heap dump's object graph. Use its
views as a sequence: locate a large keep-alive dependency, find its root path,
and inspect the data it retains.

### Find the largest keep-alive dependency

Start with MAT's dominator tree and sort it by retained size. An object
**dominates** another object when every path from a GC root to the second
object passes through the first. If `OrderCache` dominates a large group of
entries, making the cache unreachable would also make that group collectible.

Suppose the first useful result is:

```text
OrderCache
  shallow size:     96 bytes
  retained size:   3.2 GB
```

This makes the cache an important lead, not proof of a defect. The dominator
tree models reachability rather than intended ownership, and its parent-child
edges need not be direct object references.

Prefer candidates such as caches, queues, sessions, registries, and class
loaders. Arrays and collection internals often hold the bytes while another
component decides how long they remain.

### Find why the owner remains reachable

Run **Path to GC Roots** on the `OrderCache`. MAT then walks backward through
references until it finds a root:

```text
GC root: static field
          |
          v
     CacheRegistry
          |
          v
       OrderCache
          |
          v
  2,400,000 entries
```

Now the explanation is precise: a static field keeps `CacheRegistry` alive,
and the registry keeps the cache alive. Ask whether that process-long lifetime
is intended and whether the cache has an effective capacity.

Ordinary fields are usually **strong references**, so their targets stay
reachable while the root path remains. GC may clear targets reached only
through Java's weak or soft references. Excluding these special references
from a MAT search can expose the strong path preventing collection.

### Inspect what the owner retains

After identifying the owner, inspect the classes below its retained set. A
class histogram groups objects by class and reports their instance counts and
shallow-byte totals. For the same cache, it might show:

```text
owner:    OrderCache
retains:  3.2 GB

contents:
  2,400,000 OrderSummary objects
  2,400,000 map nodes
  4,900,000 byte arrays
```

The histogram describes composition, not why data survives. Here, the
dominator tree found the keep-alive dependency, the root path exposed its
process-long ownership, and the histogram showed what fills the cache.

MAT's Leak Suspects Report highlights large retained sets and likely owners.
Use it for orientation, then verify its suggestions with the dominator tree
and root paths. It does not know the application's intended lifetime policy.

## Recognize lifetime mismatches

Heap retention becomes a problem when the lifetime of stored data exceeds the
lifetime the application intended:

| Pattern            | Typical root path                        | Lifetime mismatch                  |
|--------------------|------------------------------------------|------------------------------------|
| Unbounded cache    | Service -> cache -> entries              | Cache has no effective capacity    |
| Thread-local value | Pool thread -> thread-local map -> value | Thread outlives request data       |
| Class-loader leak  | Runtime root -> old loader -> classes    | Loader survives application reload |
| Listener retention | Event source -> listeners -> component   | Source outlives retired listener   |
| Static collection  | Static field -> collection -> entries    | Class outlives stored entries      |
| Oversized query    | Request thread -> result rows            | Request retains too many rows      |

For example, a worker pool reuses its threads across many requests. If a
request stores data in a thread-local variable and never removes it, the
long-lived worker thread can preserve request-scoped data after the request
finishes:

```text
worker thread
     |
     v
thread-local map
     |
     v
finished request data
```

Fix that lifetime boundary: remove the value when the request finishes or do
not attach request state to a reusable thread.

## Compare captures only when growth is the question

One dump cannot distinguish a stable large heap from continuing growth. Begin
with lower-impact evidence such as post-collection heap trends, object counts,
or allocation profiles. If needed, capture another dump at a comparable
workload point.

```text
10:00  OrderSummary count =   400,000
11:00  OrderSummary count = 1,100,000
12:00  OrderSummary count = 1,900,000
```

Each additional dump repeats the pause and disk costs. Growth also needs
context: a cache warming toward a fixed limit can grow safely, while the same
root path without a capacity can grow until the heap fills.

## Finish with a testable explanation

A useful diagnosis connects four facts:

```text
objects consuming memory
          +
component retaining them
          +
root keeping that component reachable
          +
missing or incorrect lifetime boundary
```

For the running example: `OrderSummary` objects fill an `OrderCache`; a static
`CacheRegistry` keeps the cache reachable; and the cache lacks an effective
capacity. That explanation predicts a remedy and a validation test.

After correcting the ownership policy, repeat the workload and observe the
heap after comparable collections. The surviving heap should stabilize, and
the cache's retained set should remain within its intended bound.

Do not stop at the largest class. Follow references until they reach the
component that decides how long the data lives.

---

Return to [Troubleshooting](_index.md)
