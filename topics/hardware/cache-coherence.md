# Cache coherence

Cache coherence is the hardware mechanism that ensures multiple CPU cores maintain a consistent view of shared memory, even when they have their own private caches.

It is one of the fundamental mechanisms that makes multicore and multiprocessor systems possible.

The central problem is simple:

> What happens when two CPU cores cache the same memory location, and one of them modifies it?

## 1. The problem: multiple caches, one memory

Modern CPUs have multiple levels of cache.

Consider a processor with two cores:

```text
CPU PACKAGE
+-----------------------------------------+
|                                         |
|   +---------------+  +--------------+   |
|   |    Core 0     |  |    Core 1    |   |
|   |               |  |              |   |
|   |   L1 Cache    |  |   L1 Cache   |   |
|   |   L2 Cache    |  |   L2 Cache   |   |
|   +-------+-------+  +-------+------+   |
|           |                  |          |
|           +--------+---------+          |
|                    |                    |
|             +------+------+             |
|             |  Shared L3  |             |
|             +------+------+             |
|                    |                    |
+--------------------+--------------------+
                     |
              Memory Controller
                     |
                     v
                Main Memory
```

This simplified layout illustrates private L1/L2 caches and a shared L3 cache. Real cache hierarchies vary.

Suppose main memory contains:

```text
x = 10
```

Both cores read `x`, bringing the cache line containing it into their respective L1 caches.

```text
         Core 0                  Core 1
    +--------------+        +--------------+
    |   L1 Cache   |        |   L1 Cache   |
    |              |        |              |
    |    x = 10    |        |    x = 10    |
    +--------------+        +--------------+
            \                     /
             \                   /
              +-----------------+
              |   Main Memory   |
              |     x = 10      |
              +-----------------+
```

Everything is consistent.

Now Core 0 writes:

```text
x = 20
```

Without coherence, the system could end up with:

```text
         Core 0                  Core 1
    +--------------+        +--------------+
    |   L1 Cache   |        |   L1 Cache   |
    |              |        |              |
    |    x = 20    |        |    x = 10    |
    +--------------+        +--------------+
            \                     /
             \                   /
              +-----------------+
              |   Main Memory   |
              |     x = 10      |
              +-----------------+
```

There are now different cached values for the same address.

If Core 1 reads from its cache, it could retrieve an obsolete value indefinitely.

Cache coherence solves this problem by coordinating the copies stored in different caches.

Importantly, main memory does not need to be updated immediately. The latest data can temporarily exist only in a CPU cache.

## 2. Cache coherence operates on cache lines

A critical detail: cache coherence operates at cache-line granularity, not individual-variable granularity.

A cache line is a fixed-size block of memory transferred and managed by the cache hierarchy.

On modern x86 processors, cache lines are commonly 64 bytes.

Consider two integers:

```text
Memory:

Address
   |
   v
+--------------------------------------------------+
| Cache Line (64 bytes)                            |
+--------------------------------------------------+
| x = 10 | y = 20 | Other data...                  |
+--------------------------------------------------+
  4 B      4 B      56 B
```

Even though `x` and `y` are separate variables, they occupy the same cache line.

When a processor obtains write ownership of this line, coherence operates on the entire 64-byte block.

This detail becomes especially important when discussing false sharing, synchronization, and multicore performance.

## 3. The MESI protocol

A classic cache-coherence protocol is MESI.

MESI stands for:

- M — Modified
- E — Exclusive
- S — Shared
- I — Invalid

Each cache line has a coherence state that determines whether the line can be read or written locally and what coordination is required.

| State         | Meaning                                             | Can read? | Can write without further coherence request? |
| ------------- | --------------------------------------------------- | --------- | -------------------------------------------- |
| M (Modified)  | Sole valid cached copy, modified relative to memory | Yes       | Yes                                          |
| E (Exclusive) | Sole valid cached copy, clean                       | Yes       | Yes                                          |
| S (Shared)    | Clean copy, potentially held by other caches        | Yes       | No                                           |
| I (Invalid)   | No usable cached copy                               | No        | No                                           |

### Example: how MESI works

Start with:

```text
Main memory: x = 10

Core 0 cache: INVALID
Core 1 cache: INVALID
```

Step 1: Core 0 reads x.

Core 0 fetches the cache line containing `x`. Assuming no other cache holds it:

```text
               Core 0
          +-------------+
          |    x = 10   |
          |  State: E   |
          +-------------+
                 |
                 |
          +-------------+
          | Main Memory |
          |    x = 10   |
          +-------------+
```

Core 0 now holds the cache line in the Exclusive state.

Step 2: Core 1 reads x.

Core 1 requests the same cache line.

The coherence system recognizes that Core 0 already holds a copy. In this simplified MESI example:

```text
           Core 0                Core 1
      +-------------+       +-------------+
      |   x = 10    |       |   x = 10    |
      |  State: S   |       |  State: S   |
      +-------------+       +-------------+
              \                  /
               \                /
                +--------------+
                | Main Memory  |
                |    x = 10    |
                +--------------+
```

Both cores can read the value.

There is no problem because neither core has write ownership.

Step 3: Core 0 wants to write x = 20.

Core 0 cannot simply modify the line while Core 1 has a valid shared copy.

It must first obtain exclusive write ownership.

```text
Core 0                         Core 1
   |                               |
   | Request write ownership       |
   |------------------------------>|
   |                               |
   |                           Invalidate cached line
   |                               |
   |<------------------------------|
   |     Invalidation acknowledged |
   |                               |
   v                               v

+-------------+               +-------------+
|   x = 20    |               |   x = 10    |
|  State: M   |               |  State: I   |
+-------------+               +-------------+
```

The coherence mechanism ensures that conflicting copies are invalidated before the writer has globally effective ownership.

The result is:

```text
Core 0 cache:  x = 20, Modified
Core 1 cache:  Invalid
Main memory:   x = 10
```

Notice that main memory can still contain the old value.

This is intentional. Requiring every CPU write to immediately reach DRAM would undermine much of the performance advantage of caching.

Step 4: Core 1 reads x again.

Core 1's cached copy is invalid.

It must obtain the updated cache line.

```text
Core 1
   |
   | Read x
   v
L1 Cache
   |
   | Cache line invalid
   v
Coherence system
   |
   | Locate current owner
   v
Core 0 cache
   |
   | Supply x = 20
   v
Core 1 receives current data
```

In a basic MESI model, Core 0 can supply the modified data and transition to a shared state, with the necessary writeback or equivalent action to make the shared copies clean.

The implementation may route the data through a cache/home agent rather than directly between L1 caches.

## 4. What actually coordinates the caches?

The previous example raises an important question.

How does Core 0 know that Core 1 has a cached copy?

This is handled by the hardware coherence machinery, using mechanisms such as snooping and directories.

### Snooping

In a classic snooping architecture, coherence requests are broadcast so other caches can inspect the requested address and react.

```text
     Core 0         Core 1         Core 2
       |              |              |
     Cache 0        Cache 1        Cache 2
       |              |              |
       +--------------+--------------+
                      |
              Coherence Fabric
                      |
                      v
                 Main Memory
```

When Core 0 requests exclusive ownership of a line, other caches can observe the request and invalidate matching copies.

This is conceptually straightforward, but broadcasting every coherence request becomes expensive as processor counts increase.

### Directory-based coherence

A directory maintains information about which caches may hold a particular line and which processor has ownership.

```text
                 Coherence Directory
              +-----------------------+
              | Cache Line: 0x1000    |
              |                       |
              | Sharers: 0, 1         |
              | Owner: None           |
              +-----------+-----------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
           Cache 0                 Cache 1
           State: S                State: S
```

When Core 0 requests write ownership:

```text
Core 0
   |
   | Request exclusive ownership
   v
Directory / Home Agent
   |
   | Identify other sharers
   v
Core 1
   |
   | Invalidate copy
   | Acknowledge
   v
Directory / Home Agent
   |
   | Grant ownership
   v
Core 0
```

The directory reduces the need to broadcast every request to every processor.

Modern systems frequently employ distributed directories, snoop filters, and sophisticated coherence fabrics.

## 5. Cache coherence across CPU sockets

Cache coherence becomes even more interesting in multi-socket servers.

Consider a dual-socket NUMA system:

```text
+--------------------------+
|         SOCKET 0         |
|                          |
|    Core 0     Core 1     |
|      |          |        |
|    L1/L2      L1/L2      |
|       \        /         |
|        Shared LLC        |
|                          |
+------------+-------------+
             |
             | Cache-coherent
             | interconnect
             |
+------------+-------------+
|         SOCKET 1         |
|                          |
|    Core 2     Core 3     |
|      |          |        |
|    L1/L2      L1/L2      |
|       \        /         |
|        Shared LLC        |
|                          |
+--------------------------+
```

In a coherent multi-socket system, caches in different CPU packages still participate in a shared coherence domain.

Suppose Core 0 on Socket 0 and Core 2 on Socket 1 repeatedly update the same cache line.

```text
       SOCKET 0                  SOCKET 1

       Core 0                    Core 2
          |                         |
          v                         v
       Cache 0                   Cache 2
          |                         |
          +-----------+-------------+
                      |
                Interconnect
```

A simplified sequence:

```text
Time      Socket 0                Socket 1
--------------------------------------------------
T0        Owns line (M)           Invalid

T1        Writes x = 1            Invalid

T2        Relinquishes ownership  Requests ownership

T3        Invalid                 Owns line (M)

T4        Invalid                 Writes x = 2

T5        Requests ownership      Relinquishes ownership

T6        Owns line (M)           Invalid
```

Ownership repeatedly moves between the sockets.

This is called cache-line bouncing, or cache ping-pong.

It is expensive because it introduces coherence transactions over the inter-socket connection.

Furthermore, the cost depends on the physical distance and characteristics of the interconnect.

A shared variable with frequent writes can become a major scalability bottleneck even when there is plenty of available CPU capacity.

## 6. False sharing: a common performance problem

False sharing occurs when independent variables share a cache line and are modified by different CPU cores.

For example:

```c
struct Counters {
    long requests;
    long errors;
};
```

Assuming 8-byte `long` values, both fields could occupy the same 64-byte cache line.

```text
CACHE LINE
+------------------------------------------+
| requests | errors | Other bytes          |
+------------------------------------------+
  8 B        8 B      48 B
```

Suppose:

- Core 0 repeatedly increments `requests`.
- Core 1 repeatedly increments `errors`.

There is no logical sharing between the two counters, but there is physical sharing of the cache line.

```text
          Core 0                   Core 1
             |                        |
             v                        v
         requests++                errors++
             |                        |
             +-----------+------------+
                         |
                  Same cache line
                         |
                         v
                Ownership contention
```

Even though the cores update different variables, both need exclusive ownership of the same cache line.

The line repeatedly moves between cores.

This can severely reduce performance.

### Solution: separate hot writable data

One possible layout is:

```text
Cache Line 0
+------------------------------------------+
| requests |           Padding             |
+------------------------------------------+

Cache Line 1
+------------------------------------------+
| errors   |           Padding             |
+------------------------------------------+
```

Now the two cores can independently own and modify their respective cache lines.

Padding is not always worthwhile; it increases memory footprint and may reduce cache efficiency elsewhere.

## 7. Cache coherence is not memory consistency

This distinction is essential for concurrency programming.

Cache coherence determines how processors maintain consistent values for individual memory locations.

Memory consistency (memory ordering) determines which ordering of memory operations can be observed across processors.

Consider:

```text
Initially:

data  = 0
ready = 0
```

Core 0:

```text
data = 42
ready = 1
```

Core 1:

```text
if ready == 1:
    print(data)
```

It might appear that observing `ready = 1` guarantees observing `data = 42`.

But cache coherence alone does not establish that guarantee.

Each variable can be individually coherent while the ordering of operations across different memory locations remains insufficiently constrained.

Depending on the architecture, compiler, and language memory model, explicit synchronization may be required.

For example, release/acquire atomics can establish the required ordering.

```text
              Core 0
                 |
           Write data = 42
                 |
           Release store
             ready = 1
                 |
                 |
          synchronizes-with
                 |
                 v
              Core 1
                 |
           Acquire load
             ready == 1
                 |
                 v
           Read data = 42
```

The acquire must read the value from the corresponding release sequence for the synchronization relationship to apply.

Cache coherence is a hardware foundation for shared-memory concurrency, but it is not a substitute for atomics, locks, or memory-ordering guarantees.

## 8. What cache coherence means for software performance

Several engineering principles follow from these hardware mechanisms.

| Pattern                                               | Coherence effect                                     |
| ----------------------------------------------------- | ---------------------------------------------------- |
| Multiple cores read the same immutable data           | Efficient sharing after lines are fetched            |
| One core repeatedly writes a privately owned line     | Usually efficient; no repeated ownership transfers   |
| Multiple cores repeatedly write the same line         | Ownership contention and cache-line bouncing         |
| Independent variables share a frequently written line | False sharing                                        |
| Per-core counters                                     | Reduce ownership contention                          |
| Cross-socket shared writes                            | Potentially expensive inter-socket coherence traffic |

This motivates architectural techniques such as per-core data structures, sharded counters, thread-local aggregation, batching, and reducing cross-core synchronization.

There is an important distinction between sharing data and sharing write ownership.

Multiple CPUs can read the same data efficiently. Frequent changes to write ownership are often what make shared-memory access expensive.

## 9. MESI vs. MOESI

MESI is the foundational teaching model, but it is not the only coherence protocol.

MOESI adds an additional state:

O — Owned

This state allows a cache to retain responsibility for dirty data while other caches hold shared copies.

```text
                  Core 0
             +-------------+
             |   x = 20    |
             |  State: O   |
             +-------------+
                    |
                    | Shared dirty data
                    |
             +-------------+
             |   x = 20    |
             |  State: S   |
             +-------------+
                  Core 1

               Main Memory
                 x = 10
```

The owner is responsible for ensuring the modified data is eventually written back, while readers can hold valid shared copies.

## Key takeaways

1. Cache coherence maintains consistency across private CPU caches, without requiring every write to immediately reach DRAM.
2. Coherence operates at cache-line granularity, generally 64 bytes on modern x86 systems.
3. MESI tracks whether a line is Modified, Exclusive, Shared, or Invalid.
4. To modify a shared line, a CPU generally needs to obtain exclusive write ownership.
5. Cache-line ownership can move between cores and sockets, introducing latency and interconnect traffic.
6. False sharing is an important source of otherwise surprising multicore performance problems.
7. Cache coherence and memory consistency are related but different mechanisms.
