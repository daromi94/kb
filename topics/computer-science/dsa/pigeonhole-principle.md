# Pigeonhole principle

The Pigeonhole Principle is a fundamental mathematical principle stating that:

> **If more objects are distributed among fewer containers, at least one container must hold more than one object.**

The name comes from the idea of putting pigeons into pigeonholes (small compartments).

## 1. Basic intuition

Suppose there are 5 pigeons and only 4 pigeonholes.

```text
Pigeons                 Pigeonholes

   A ------+
           +----------> [ A, B ]
   B ------+

   C -----------------> [ C ]

   D -----------------> [ D ]

   E -----------------> [ E ]

5 pigeons               4 pigeonholes
```

No matter how the pigeons are distributed, at least one pigeonhole must contain two or more pigeons.

**This is a mathematical guarantee, not a probability.**

## 2. Generalized Pigeonhole Principle

For `N` objects distributed among `M` containers, at least one container must contain:

```text
ceil(N / M)
```

objects.

For example, if 100 tasks are assigned to 8 queues:

```text
ceil(100 / 8) = 13
```

**At least one queue must contain 13 or more tasks, regardless of the assignment strategy.**

Notice that the principle says nothing about which queue will contain those tasks.

## 3. Applications in operating systems

### Hash-table collisions

Suppose a kernel data structure maps 1,000 objects into 256 hash buckets.

```text
Objects                 Hash buckets

Object 1  ------------> [ Bucket 0 ]
Object 2  ------------> [ Bucket 1 ]
Object 3  -----+
               +------> [ Bucket 2 ]
Object 4  -----+
   ...                      ...
Object 1000 ----------> [ Bucket 255 ]
```

By the Pigeonhole Principle, at least one bucket must contain:

```text
ceil(1000 / 256) = 4
```

objects.

In fact, collisions are inevitable because there are more objects than buckets.

This explains why hash tables need collision-handling mechanisms such as chaining or open addressing.

### CPU scheduling

Consider 10 runnable CPU-bound threads competing for 4 CPU cores.

If the threads are assigned to cores:

```text
Core 0: [ T1, T2, T3 ]

Core 1: [ T4, T5 ]

Core 2: [ T6, T7, T8 ]

Core 3: [ T9, T10 ]
```

At least one core must have 3 or more assigned threads.

Since each core can execute only one thread at a time (assuming one hardware execution context per core), the threads assigned to that core must share CPU execution time.

**The principle guarantees contention under those assumptions, but does not determine scheduling fairness, latency, or actual CPU utilization.**

## 4. Why is it important?

The Pigeonhole Principle is useful because it establishes what is mathematically unavoidable, independently of the implementation.

It appears in:

- Hash-table collisions.
- Finite identifier and address spaces.
- Resource allocation.
- Queue distribution and worst-case load.
- Information theory and lossless compression.
- Data structures and algorithms.

For example, it proves that no lossless compression algorithm can make every possible input smaller. There are simply not enough shorter binary strings to represent all longer binary strings uniquely.

The key insight: **When the number of distinguishable objects exceeds the number of available destinations, some destination must be shared.** No algorithm can eliminate this fundamental constraint without increasing the number of destinations, restricting the inputs, or changing the representation.
