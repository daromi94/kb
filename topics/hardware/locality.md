# Locality

Locality is the tendency of a program to access the same memory locations, or nearby memory locations, within a relatively short period of time.

It is one of the most important principles behind CPU cache design and software performance.

The central idea is:

> Memory accesses are not completely random. Programs often reuse recently accessed data or access data located near it.

Modern CPUs exploit this behavior to avoid repeatedly accessing slower memory.

## 1. Why locality matters

Consider a CPU with the following simplified memory hierarchy:

```text
                  CPU CORE
                     |
                     v
              +-------------+
              |  Registers  |
              +-------------+
                     |
                     v
              +-------------+
              |  L1 Cache   |  Fastest cache
              +-------------+
                     |
                     v
              +-------------+
              |  L2 Cache   |
              +-------------+
                     |
                     v
              +-------------+
              |  L3 Cache   |
              +-------------+
                     |
                     v
              +-------------+
              |    DRAM     |  Much slower
              +-------------+
```

The CPU cannot keep all of main memory in its caches because caches are relatively small.

Instead, it keeps copies of selected memory blocks.

The effectiveness of this strategy depends heavily on locality.

For example:

```text
Program A:

Read A
Read A
Read A
Read A
Read A

        |
        v

The data can remain in cache.


Program B:

Read A
Read B
Read C
Read D
Read E

        |
        v

Potentially more cache misses if addresses are far apart.
```

Program A exhibits reuse. Program B might or might not benefit from caching, depending on whether the addresses share cache lines and whether those lines are already resident.

The important distinction is not the number of memory operations, but how much data must move through the memory hierarchy to satisfy those operations.

## 2. The two fundamental types of locality

There are two principal kinds:

1. Temporal locality — reusing the same memory location.
2. Spatial locality — accessing nearby memory locations.

### Temporal locality

Temporal locality means that data accessed recently is likely to be accessed again soon.

Consider:

```c
int counter = 0;

for (int i = 0; i < 1000; i++) {
    counter++;
}
```

Conceptually, the program repeatedly accesses the same variable.

```text
Time

T0      Access counter
              |
T1      Access counter
              |
T2      Access counter
              |
T3      Access counter
              |
T4      Access counter
              |
              v

Same memory location accessed repeatedly
```

If `counter` is stored in memory and remains in cache, repeated accesses can be satisfied without going to DRAM.

In practice, an optimizing compiler might keep `counter` entirely in a register, eliminating those memory accesses. This is an even more efficient form of data reuse.

Temporal locality is particularly useful in algorithms that repeatedly operate on a relatively small working set.

### Spatial locality

Spatial locality means that accessing a particular memory address makes accesses to nearby addresses more likely.

Consider:

```c
int numbers[16];

for (int i = 0; i < 16; i++) {
    sum += numbers[i];
}
```

Assume each integer occupies 4 bytes and the array begins on a 64-byte boundary.

```text
MAIN MEMORY

Address
   |
   v
0x1000  +-----------------------------------------+
        | numbers[0]  | numbers[1]  | numbers[2]  |
        +-----------------------------------------+
        | numbers[3]  | numbers[4]  | ...         |
        +-----------------------------------------+
        | numbers[13] | numbers[14] | numbers[15] |
0x103F  +-----------------------------------------+

        One 64-byte cache line
```

When `numbers[0]` is accessed and the cache line is absent, the processor can fetch the entire 64-byte line.

The remaining elements are then already present in that line.

```text
Access        Result (assuming initially uncached)
--------------------------------------------------
numbers[0]    Cache miss, fetch 64-byte line
numbers[1]    Cache hit
numbers[2]    Cache hit
numbers[3]    Cache hit
...
numbers[15]   Cache hit
```

This is why CPU caches operate on cache lines rather than individual variables.

A program accessing four bytes might obtain 64 bytes because the hardware anticipates that neighboring data may be needed soon.

## 3. Temporal vs. spatial locality

These concepts are related but distinct.

```text
TEMPORAL LOCALITY

Memory:
+----+----+----+----+----+
| A  | B  | C  | D  | E  |
+----+----+----+----+----+
  ^    ^    ^
  |    |    |
  A -> B -> A -> C -> A

Repeated access to A.


SPATIAL LOCALITY

Memory:
+----+----+----+----+----+
| A  | B  | C  | D  | E  |
+----+----+----+----+----+
  |    |    |    |    |
  +----+----+----+----+
            |
            v
  A -> B -> C -> D -> E

Accesses to adjacent locations.
```

| Property             | Temporal locality                  | Spatial locality                             |
| -------------------- | ---------------------------------- | -------------------------------------------- |
| Fundamental behavior | Reuse the same location            | Access nearby locations                      |
| Typical example      | Repeatedly reading a variable      | Sequential array traversal                   |
| Main cache advantage | Avoid fetching the same data again | Use more of each fetched cache line          |
| Common optimization  | Reuse loaded data before eviction  | Store and traverse related data contiguously |

A program can exhibit both simultaneously.

## 4. Locality and CPU cache efficiency

Consider two data structures containing 1,024 integers.

### Case A: Contiguous array

```c
int numbers[1024];
```

Memory layout:

```text
+--------+--------+--------+--------+
| int 0  | int 1  | int 2  | int 3  |
+--------+--------+--------+--------+
| int 4  | int 5  | int 6  | int 7  |
+--------+--------+--------+--------+
| ...                      | int N  |
+--------+--------+--------+--------+
```

With 4-byte integers and 64-byte cache lines, each line contains 16 integers when properly aligned.

Traversing the entire array requires accessing 64 distinct cache lines.

### Case B: Linked list

```c
struct Node {
    int value;
    struct Node *next;
};
```

Individual nodes might be scattered throughout the heap.

```text
Node A                 Node C
0x1000                 0x9000
+---------+            +---------+
| value   |            | value   |
| next ---+----+       | next    |
+---------+    |       +---------+
               |           ^
               v           |
             Node B        |
             0x5000        |
             +---------+   |
             | value   |   |
             | next ---+---+
             +---------+
```

Traversing the list can involve fetching a new cache line for each node.

Even worse, the address of the next node is stored in the current node. This creates a dependency:

```text
Load Node A
    |
    v
Read pointer to B
    |
    v
Load Node B
    |
    v
Read pointer to C
    |
    v
Load Node C
```

The processor may be unable to issue the next load until the previous pointer has been retrieved.

This is known as pointer chasing.

For equal numbers of elements, the array often enjoys better spatial locality and makes memory accesses easier for hardware prefetchers to predict.

However, linked lists are not inherently cache-unfriendly: nodes allocated consecutively in an arena, for example, can have much better locality than independently allocated nodes.

## 5. Working sets: the connection between locality and cache capacity

An important related concept is the working set.

The working set is the collection of memory blocks actively accessed by a program during some interval.

Suppose a CPU has:

```text
L1 Cache:        32 KiB
L2 Cache:         1 MiB
L3 Cache:        32 MiB
Main Memory:     64 GiB
```

And an algorithm repeatedly accesses 16 KiB of data.

```text
CPU CORE
    |
    v
+---------------------+
|      L1 Cache       |
|                     |
| Capacity: 32 KiB    |
|                     |
| Working set: 16 KiB |
+---------------------+
```

After the data is loaded, it may remain in L1 because the working set fits comfortably, assuming no significant set conflicts, eviction pressure, or interference.

Now consider an algorithm operating repeatedly on 128 MiB.

```text
Working set: 128 MiB
           |
           +-- L1:  32 KiB   Too small
           |
           +-- L2:   1 MiB   Too small
           |
           +-- L3:  32 MiB   Too small
           |
           +-- DRAM
```

Repeated operations over this working set may generate substantial memory traffic if the access pattern provides little reuse before eviction.

The important principle is:

Temporal locality helps when data is reused while it is still cached.

Reusing an element after millions of unrelated accesses may offer little cache benefit if it has already been evicted.

## 6. How algorithms improve locality

One of the best illustrations is matrix traversal.

In C, two-dimensional arrays are stored in row-major order.

Consider:

```c
int matrix[3][4];
```

Physical memory layout:

```text
CONTIGUOUS MEMORY

+-----+-----+-----+-----+
| 0,0 | 0,1 | 0,2 | 0,3 |
+-----+-----+-----+-----+
| 1,0 | 1,1 | 1,2 | 1,3 |
+-----+-----+-----+-----+
| 2,0 | 2,1 | 2,2 | 2,3 |
+-----+-----+-----+-----+
```

### Row-major traversal

```c
for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLS; j++) {
        sum += matrix[i][j];
    }
}
```

Access order:

```text
Row 0: (0,0) -> (0,1) -> (0,2) -> (0,3)
Row 1: (1,0) -> (1,1) -> (1,2) -> (1,3)
Row 2: (2,0) -> (2,1) -> (2,2) -> (2,3)
```

Excellent spatial locality: neighboring array elements are accessed successively.

### Column-major traversal

```c
for (int j = 0; j < COLS; j++) {
    for (int i = 0; i < ROWS; i++) {
        sum += matrix[i][j];
    }
}
```

Access order:

```text
Column 0: (0,0) -> (1,0) -> (2,0)
Column 1: (0,1) -> (1,1) -> (2,1)
Column 2: (0,2) -> (1,2) -> (2,2)
Column 3: (0,3) -> (1,3) -> (2,3)
```

Within each column, successive accesses are separated by an entire row.

For large matrices, this can lead to poorer cache-line utilization, increased misses, and less effective prefetching.

The differences are especially pronounced when the row stride is large relative to a cache line.

## 7. Cache blocking: combining temporal and spatial locality

Cache blocking, also called tiling, is an algorithmic technique that divides a large problem into smaller regions that fit in cache.

Instead of processing an entire large matrix in one pass, an algorithm processes smaller blocks.

```text
LARGE MATRIX

+-----------+-----------+-----------+
|           |           |           |
|  Block A  |  Block B  |  Block C  |
|           |           |           |
+-----------+-----------+-----------+
|           |           |           |
|  Block D  |  Block E  |  Block F  |
|           |           |           |
+-----------+-----------+-----------+
|           |           |           |
|  Block G  |  Block H  |  Block I  |
|           |           |           |
+-----------+-----------+-----------+
```

For a computation with multiple passes over the same data, the goal is to perform as much work as possible on a block while that block remains cached.

```text
Load Block A into cache
    |
    v
Compute step 1
    |
    v
Compute step 2
    |
    v
Compute step 3
    |
    v
Move to Block B
```

This increases temporal reuse while keeping the active working set small.

Blocking is widely used in matrix multiplication, numerical computing, image processing, and database execution engines.

## 8. Locality and hardware prefetching

Locality is related to another important CPU mechanism: hardware prefetching.

When the CPU detects predictable access patterns, it can fetch cache lines before instructions actually request them.

Consider:

```text
CPU loads cache line 0
    |
    v
CPU loads cache line 1
    |
    v
CPU loads cache line 2
    |
    v
Hardware recognizes
sequential pattern
    |
    v
Prefetch cache line 3
    |
    v
Prefetch cache line 4
```

When the application reaches line 3, the data may already be available in a nearby cache.

This can hide a significant portion of memory-access latency.

But there is a distinction:

- Locality is a property of the program's memory-access pattern.
- Prefetching is a hardware technique for predicting future accesses and moving data closer to the CPU.

Sequential scanning often has excellent spatial locality and prefetchability, even if every element is read only once and temporal locality is low.

Modern Intel hardware prefetchers support a variety of sequential and strided access patterns.

## 9. Locality in multicore and NUMA systems

So far, locality has concerned which data remains in cache and which addresses are accessed together.

In multiprocessor systems, another dimension matters: where the data physically resides.

Consider:

```text
    SOCKET 0                  SOCKET 1
    +-----------+             +-----------+
    |  Core 0   |             |  Core 1   |
    +-----+-----+             +-----+-----+
          |                         |
          |     Interconnect        |
          +-------------+-----------+
          |             |
          v             v
      +-------+     +-------+
      | RAM 0 |     | RAM 1 |
      +-------+     +-------+
```

If Core 0 frequently accesses memory attached to Socket 0, those accesses have good NUMA (Non-Uniform Memory Access) locality.

If it accesses memory attached to Socket 1, cache misses may require remote memory accesses.

This is different from temporal and spatial locality:

| Locality type | Fundamental question                                 |
| ------------- | ---------------------------------------------------- |
| Temporal      | Will the same data be reused soon?                   |
| Spatial       | Will nearby data be accessed soon?                   |
| NUMA          | Is the data located near the processor accessing it? |

A NUMA-remote access can still hit in a local cache. The NUMA placement matters particularly when requests must travel beyond the local caches.

There is also a coherence dimension: data repeatedly modified by different cores can bounce between their caches, even if the underlying memory allocation has favorable NUMA placement.

## 10. Locality as a software-design principle

The same hardware principles influence data structure and software architecture choices.

| Design choice               | Locality implication                                          |
| --------------------------- | ------------------------------------------------------------- |
| Contiguous arrays           | Usually good spatial locality                                 |
| Scattered linked structures | Potentially poor spatial locality                             |
| Structure of Arrays (SoA)   | Efficient when processing selected fields across many records |
| Array of Structures (AoS)   | Efficient when processing most fields of each record together |
| Cache blocking              | Improves reuse within a bounded working set                   |
| Per-core data structures    | Can improve locality and reduce coherence contention          |
| Sequential scans            | Often hardware-prefetch friendly                              |
| Random pointer chasing      | Often latency-bound and difficult to prefetch                 |

The choice between AoS and SoA is particularly relevant to columnar data systems such as Apache Arrow. If a computation only needs one field from each record, grouping that field's values together often means fewer irrelevant bytes are fetched into the cache.

The best layout depends on the actual access pattern, not merely whether the data is contiguous.

## 11. The deeper principle: move data as little as possible

A useful way to understand locality is through data movement.

```text
              COMPUTATION
                   |
                   v
          Is data in registers?
              /         \
            Yes          No
             |            |
           Reuse      Check cache
                          |
                          v
                     Cache hit?
                      /     \
                    Yes      No
                     |        |
                   Reuse   Fetch data
                              |
                              v
                       Higher latency
                       More data traffic
```

Good locality can reduce the number of expensive data transfers, improve effective cache hit rates, and make better use of limited memory bandwidth.

But minimizing misses is not the only consideration: a streaming algorithm can perform very well despite little temporal reuse, provided its access pattern makes effective use of bandwidth and prefetching.

The real performance objective is to minimize the cost of obtaining the data needed for computation.

## Key takeaways

1. Locality describes how closely related a program's memory accesses are in time and address space.
2. Temporal locality is reuse of the same data; spatial locality is reuse of nearby memory.
3. Cache lines exploit spatial locality by fetching contiguous blocks.
4. Working-set size determines whether temporal reuse is likely to result in cache hits.
5. Contiguous data layouts, cache blocking, and predictable access patterns often improve performance.
6. NUMA locality adds a physical-placement dimension in multi-socket systems.
7. Locality is one of the foundational principles of data-oriented programming and CPU-efficient algorithm design.
