# Heap dump analysis

A heap dump records the Java objects in a running Java Virtual Machine (JVM)
and the references between them. Use it when the investigation needs to
explain which objects occupy the heap and why garbage collection cannot
reclaim them.

The central rule is:

> **A large object is only a symptom until its reference path identifies the
> owner that keeps it alive.**

## A heap dump is an object graph

The **Java heap** stores application objects managed by garbage collection
(GC). GC reclaims an object only when no live execution path can reach it.

A heap dump represents those objects as a graph:

```text
GC root
   |
   v
CacheManager
   |
   v
ConcurrentHashMap
   |
   +--> entry --> OrderSummary
   +--> entry --> OrderSummary
   +--> entry --> OrderSummary
```

A **GC root** is a starting point that the JVM treats as reachable. Common
roots include active thread stacks, static fields, and references held by JVM
runtime structures.

The graph answers two different size questions:

- **Shallow size** is the memory occupied by one object itself.
- **Retained size** estimates how much heap becomes collectible if that object
  and the objects reachable only through it disappear.

A map object may have a small shallow size while retaining gigabytes through
its entries. Retained size is therefore the useful starting point for an
ownership investigation.

## Decide which state to capture

A dump is most useful when it represents the condition under investigation.
Three capture strategies answer different questions:

| Capture strategy       | What it preserves                         |
|------------------------|-------------------------------------------|
| At failure             | The object graph when allocation failed   |
| During controlled load | A reproducible point for comparison       |
| After cleanup activity | Objects that survive the expected cleanup |

Forcing a collection before a dump changes the state and may pause the
application. It can remove transient objects, but it can also erase evidence
about a burst that caused the failure. Choose that operation only when the
question specifically concerns the **live set**: the objects that remain
reachable after collection.

From a running JVM, ask the `jcmd` diagnostic utility to write the object graph
to a file:

```bash
jcmd <pid> GC.heap_dump /var/dumps/orders-service.hprof
```

A heap dump can be large and its creation can pause or slow the JVM. Verify
free disk space, write to persistent storage, and understand the production
impact before capture.

If the JVM exhausts the Java heap and throws `OutOfMemoryError`, automatic
capture preserves evidence that may vanish after restart:

```text
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/dumps
```

This mechanism applies to Java heap exhaustion. It does not produce a heap
dump for every form of `OutOfMemoryError`, such as failure to create a native
thread.

## Follow ownership, not object counts

Eclipse Memory Analyzer (MAT) reads heap dumps and calculates object-graph
relationships. Its views answer a sequence of increasingly specific
questions.

### 1. Which objects retain the most memory?

The **dominator tree** groups objects by ownership. Object A dominates object B
when every path from a GC root to B passes through A. Removing A therefore
breaks the only route that keeps B reachable.

Sort the dominator tree by retained size. Start with application-level owners
such as caches, sessions, queues, registries, and class loaders. A surviving
class loader matters because it owns the classes and metadata it defined.
Large arrays and collection internals often store the data but do not decide
its lifetime.

### 2. Why is the suspected owner still reachable?

Use **Path to GC Roots** on the suspected object. This view walks backward
from the object to the root that keeps it alive.

```text
static field
    |
    v
CacheRegistry
    |
    v
ordersByCustomer
    |
    v
2,400,000 map entries
```

The path replaces a vague observation with a specific cause: a static registry
owns an unbounded map of customer entries.

A **strong reference** normally keeps its target reachable. **Weak and soft
references** allow GC to clear their targets under defined conditions.
Excluding those special references from a path search can reveal the strong
reference that controls the object's lifetime.

### 3. Which classes make up the retained data?

A **class histogram** groups objects by class and reports instance counts and
shallow bytes. Use it to describe the contents below a dominator.

For example:

```text
owner:    OrderCache
retains:  3.2 GB

contents:
  2,400,000 OrderSummary objects
  2,400,000 map nodes
  4,900,000 byte arrays
```

The histogram explains composition. The dominator tree and root path explain
ownership. Neither view replaces the other.

### 4. Does the automated report support the same explanation?

MAT's Leak Suspects Report highlights large retained sets and their owners.
Use it for orientation, then verify its suggestion in the dominator tree and
reference paths. An automated suspect is evidence, not the final cause.

## Recognize ownership patterns

Common heap problems differ mainly in who controls object lifetime:

| Pattern            | Typical root path                        | Lifetime mismatch                  |
|--------------------|------------------------------------------|------------------------------------|
| Unbounded cache    | Service -> cache -> entries              | Cache has no effective capacity    |
| Thread-local value | Worker thread -> ThreadLocalMap -> value | Pool thread outlives request data  |
| Class-loader leak  | Runtime root -> old loader -> classes    | Old loader survives app reload     |
| Listener retention | Event source -> listeners -> component   | Source outlives retired listener   |
| Static collection  | Class root -> static collection          | Class outlives stored entries      |
| Oversized query    | Request thread -> result rows            | Request materializes too many rows |

Arrays and strings often dominate shallow-byte totals because they hold the
payload. Walk upward until the path reaches the component that chose to retain
them.

For a thread-local value, the important path is:

```text
long-lived pool thread
          |
          v
ThreadLocalMap entry
          |
          v
request-scoped object survives after the request
```

The corrective action belongs at the lifetime boundary: remove the value when
the request finishes, or avoid placing request state on a reusable thread.

## Compare dumps when growth matters

One dump shows ownership at one moment, but it cannot distinguish a stable
large heap from continued growth. Capture another dump at a comparable
workload point to see which classes and retained sets increased.

```text
10:00  OrderSummary count =   400,000
11:00  OrderSummary count = 1,100,000
12:00  OrderSummary count = 1,900,000
```

Comparison narrows the search, but growth still needs context. A cache that is
warming toward a fixed capacity can grow safely. A cache with no capacity and
the same root path can grow until the heap fills.

## Finish with a testable explanation

A complete heap diagnosis names four things:

```text
objects growing
      +
owner retaining them
      +
root keeping the owner alive
      +
missing or incorrect lifetime boundary
```

After changing the ownership policy, repeat the workload. The live set should
stabilize, the retained set should remain bounded, and collection should
recover the expected space.

Do not stop at the largest class. Follow the reference path until it reaches
the component that controls lifetime.

---

Return to [Troubleshooting](_index.md)
