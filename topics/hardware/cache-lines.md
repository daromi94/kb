# Cache lines

A cache line is the smallest unit of data that a CPU cache typically stores, transfers, and manages for cache coherence.

Modern x86 processors commonly use 64-byte cache lines.

The important idea is:

> When a CPU requests a single byte from memory, it generally brings the entire cache line containing that byte into its cache, rather than fetching only that byte.

This design is fundamental to CPU performance, memory bandwidth, cache efficiency, and cache coherence.

## 1. What is a cache line?

Consider a region of main memory containing 256 bytes.

A CPU with 64-byte cache lines divides this address range into four aligned blocks:

```text
MAIN MEMORY

Address
  |
  v
0x1000  +----------------------------------+
        |          Cache Line 0            |
        |            64 bytes              |
0x103F  +----------------------------------+

0x1040  +----------------------------------+
        |          Cache Line 1            |
        |            64 bytes              |
0x107F  +----------------------------------+

0x1080  +----------------------------------+
        |          Cache Line 2            |
        |            64 bytes              |
0x10BF  +----------------------------------+

0x10C0  +----------------------------------+
        |          Cache Line 3            |
        |            64 bytes              |
0x10FF  +----------------------------------+
```

Each cache line corresponds to a contiguous, aligned region of memory.

Suppose a CPU executes:

```c
int x = array[0];
```

Assume `array[0]` occupies addresses `0x1000` through `0x1003`.

If the data is not cached, the processor generally fetches the complete cache line:

```text
CPU requests 4 bytes
       |
       v
Address 0x1000
       |
       v
+--------------------------------------+
|               64 bytes               |
+--------------------------------------+
| 4 B | 60 B                           |
+--------------------------------------+
  ^
  |
Requested integer
```

The CPU needs only four bytes, but caching the surrounding bytes makes subsequent nearby accesses faster.

An important distinction: a cache line can be fetched from L2 or L3 rather than DRAM if another cache level already contains it.

## 2. Why cache 64 bytes instead of individual values?

The answer is spatial locality.

Spatial locality is the observation that programs often access memory addresses near addresses they recently accessed.

Consider:

```c
int numbers[16] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
```

Assume each integer occupies four bytes and the array begins at a 64-byte-aligned address.

```text
ONE CACHE LINE
+--------------------------------------------------+
|  1 |  2 |  3 |  4 |  5 |  6 |  7 |  8 | ... | 16 |
+--------------------------------------------------+

Each integer = 4 bytes, 16 x 4 = 64 bytes
```

Now consider:

```c
for (int i = 0; i < 16; i++) {
    sum += numbers[i];
}
```

The first access might miss in L1 and cause the cache line to be fetched.

The remaining 15 integers are already present in that same line.

```text
array[0]  ---> Cache miss (fetch 64 bytes)
array[1]  ---> Cache hit
array[2]  ---> Cache hit
array[3]  ---> Cache hit
...
array[15] ---> Cache hit
```

This assumes the line remains cached and no competing activity invalidates or replaces it.

Instead of independently fetching 16 integers from a distant cache level or DRAM, a single line fill can provide them all.

This is one reason sequential memory access is often extremely efficient.

## 3. How cache lines move through the memory hierarchy

Consider a processor with three cache levels.

```text
              CPU CORE
          +--------------+
          |              |
          | Load address |
          |    0x1004    |
          +------+-------+
                 |
                 v
          +--------------+
          |   L1 Cache   |
          |              |
          |  64B lines   |
          +------+-------+
                 |
              L1 miss
                 |
                 v
          +--------------+
          |   L2 Cache   |
          |              |
          |  64B lines   |
          +------+-------+
                 |
              L2 miss
                 |
                 v
          +--------------+
          |   L3 Cache   |
          |              |
          |  64B lines   |
          +------+-------+
                 |
              L3 miss
                 |
                 v
          +--------------+
          |     DRAM     |
          +--------------+
```

This is a conceptual lookup path; real implementations can perform some operations in parallel, use coherence transfers, and fetch data through additional buffers.

Suppose the load accesses address `0x1004`.

The processor determines which cache line contains the address.

For a 64-byte line:

```text
Line address = floor(Address / 64) * 64
```

Thus:

```text
Requested address: 0x1004

Cache line start:  0x1000
Cache line end:    0x103F

Offset within line: 4 bytes
```

Once the cache line is available, the processor extracts the requested bytes.

The cache line is the unit of cache storage and transfer, but individual loads can consume much smaller quantities of data.

## 4. What is actually stored inside a cache?

A cache does not simply contain a giant array of raw memory bytes.

Each cache-line entry also needs metadata.

Conceptually:

```text
CACHE ENTRY
+--------------------------------------------+
| Tag | Valid | Dirty | Coherence state      |
+--------------------------------------------+
| DATA 64 bytes                              |
|                                            |
+--------------------------------------------+
```

The components serve different purposes:

| Component         | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| Data              | Cached memory contents                                       |
| Tag               | Identifies which memory block is represented                 |
| Valid bit         | Indicates whether the entry contains usable data             |
| Dirty information | Indicates modified data that must eventually be written back |
| Coherence state   | Tracks access permissions and sharing between cores          |

These metadata fields are conceptual; their exact representation varies between processors.

For example, MESI uses coherence states such as Modified, Exclusive, Shared, and Invalid.

The important distinction is that the 64-byte cache-line size refers to the data block, not necessarily the total physical storage required for data plus metadata.

## 5. How many cache lines fit in a CPU cache?

Consider a hypothetical L1 data cache with these characteristics:

```text
L1 Data Cache

Capacity:        32 KiB
Cache line size: 64 bytes
Associativity:   8-way
```

The number of cache-line slots is:

```text
(32 * 1024) / 64 = 512
```

Therefore:

```text
L1 DATA CACHE
+--------------------------------------+
| Cache line 0      | 64 bytes         |
+--------------------------------------+
| Cache line 1      | 64 bytes         |
+--------------------------------------+
| Cache line 2      | 64 bytes         |
+--------------------------------------+
|                 ...                  |
+--------------------------------------+
| Cache line 511    | 64 bytes         |
+--------------------------------------+

Total: 512 cache-line slots
```

However, those 512 entries are not necessarily interchangeable.

An 8-way set-associative cache divides them into:

```text
512 / 8 = 64 sets
```

```text
32 KiB L1 DATA CACHE

            8 ways per set
       +----+--- +-----+----+
Set 0  | L0 | L1 | ... | L7 |
       +----+----+-----+----+
Set 1  | L0 | L1 | ... | L7 |
       +----+----+-----+----+
Set 2  | L0 | L1 | ... | L7 |
       +----+----+-----+----+
       ...
       +----+----+-----+----+
Set 63 | L0 | L1 | ... | L7 |
       +----+----+-----+----+
```

Each set can hold eight cache lines with different memory addresses that map to that set.

If nine simultaneously needed memory blocks map to the same set, at least one cannot remain resident in that set, even if other sets are underutilized.

That is one source of conflict cache misses.

## 6. What happens when a CPU writes to a cache line?

Reading is only part of the story.

Suppose a cache line contains:

```text
Main memory:

+-----------------------------+
|  10  |  20  |  30  | ...    |
+-----------------------------+
```

The CPU loads the line:

```text
L1 Cache:

+-----------------------------+
|  10  |  20  |  30  | ...    |
+-----------------------------+
```

Now the processor executes:

```c
numbers[0] = 99;
```

In a typical write-back cache, it modifies the relevant bytes in its cached copy:

```text
L1 Cache:

+-----------------------------+
|  99  |  20  |  30  | ...    |
+-----------------------------+

State: Modified
```

Meanwhile, main memory can still contain:

```text
DRAM:

+-----------------------------+
|  10  |  20  |  30  | ...    |
+-----------------------------+
```

The cache line is now dirty: it has newer data than its backing memory.

The CPU does not have to write the entire line to DRAM immediately. The modified contents can remain cached and be written back later, such as during eviction.

Notice that the CPU changed only four bytes in this example. The whole line participates in coherence and eventual writeback, but a store does not necessarily overwrite every byte.

## 7. Connection to cache coherence

Cache lines are also the unit of coherence.

Consider two CPU cores:

```text
CORE 0                      CORE 1
+----------------+          +----------------+
| L1 Cache       |          | L1 Cache       |
|                |          |                |
| Cache Line A   |          | Cache Line A   |
| State: Shared  |          | State: Shared  |
+----------------+          +----------------+
```

Both cores have copies of the same 64-byte line.

Now Core 0 wants to modify four bytes.

```text
CORE 0                              CORE 1
   |                                   |
   | Request exclusive ownership       |
   +---------------------------------->|
   |                                   |
   |                              Invalidate Cache Line A
   |                                   |
   |<----------------------------------+
   |       Acknowledgment              |
   v                                   v

Line A: Modified                  Line A: Invalid
```

Even though only four bytes are modified, Core 1 loses access to its entire cached line until it obtains an updated copy.

This is a critical consequence of cache-line granularity.

### False sharing

Suppose:

```c
struct Counters {
    long requests;
    long errors;
};
```

Both counters occupy the same line, and two cores modify different counters.

```text
CACHE LINE (64 bytes)
+-------------------------------------+
| requests | errors |     Padding     |
+-------------------------------------+
     ^         ^
     |         |
   Core 0    Core 1
```

Although the variables are logically independent, ownership of their shared cache line may repeatedly move between cores.

This is false sharing, a common multicore scalability problem.

## 8. Why alignment matters

Cache lines have fixed boundaries.

For a 64-byte cache line:

```text
Line 0: 0x1000 - 0x103F
Line 1: 0x1040 - 0x107F
```

Consider an 8-byte value starting at address `0x103C`.

```text
MEMORY

Line 0            Line 1
+---------------+ +---------------+
| ... | A A A A | | A A A A | ... |
+---------------+ +---------------+
      <---- 8-byte value --->
```

The value spans two cache lines.

A load may therefore need portions of two different cache lines.

These are called split-line accesses.

On modern Intel processors, split loads have dedicated handling, but they can still introduce performance overhead.

Proper alignment helps reduce such accesses and can also help keep independently modified data in separate lines.

However, alignment alone does not guarantee better performance. Padding can waste memory and reduce cache capacity available for useful data.

## 9. Cache lines vs. memory pages

Cache lines and pages solve different problems.

A memory page is a unit used by the virtual memory system for address translation, mapping, and protection.

A cache line is a unit used by hardware caches.

Consider a typical 4 KiB memory page and 64-byte cache lines:

```text
4 KiB PAGE
+---------------------------------------+
| Cache Line 0    | 64 bytes            |
+---------------------------------------+
| Cache Line 1    | 64 bytes            |
+---------------------------------------+
| Cache Line 2    | 64 bytes            |
+---------------------------------------+
| Cache Line 3    | 64 bytes            |
+---------------------------------------+
|                ...                    |
+---------------------------------------+
| Cache Line 63   | 64 bytes            |
+---------------------------------------+
```

A 4 KiB page contains 64 regions of 64 bytes each.

| Property           | Cache line                      | Memory page                              |
| ------------------ | ------------------------------- | ---------------------------------------- |
| Typical size       | 64 B on x86                     | 4 KiB, with larger page options          |
| Primary purpose    | Caching and coherence           | Virtual memory management                |
| Hardware mechanism | Cache hierarchy                 | MMU and page tables                      |
| Transfers          | Cache line fills and writebacks | Page-granular mapping and fault handling |

A page fault can result in allocating or loading an entire page, but it does not mean every cache line of that page must immediately enter the CPU caches.

## 10. Why not use larger cache lines?

An interesting hardware design question is why processors commonly use 64-byte cache lines instead of, say, 256-byte lines.

There is a trade-off.

Smaller cache lines

- Less unnecessary data transferred for sparse accesses.
- More tags and metadata needed for a given cache capacity.
- Potentially more individual misses for sequential accesses.

Larger cache lines

- Better amortization when adjacent bytes are used.
- Less tag overhead relative to data capacity.
- More wasted bandwidth and cache space when nearby bytes are not used.
- Larger coherence granularity, potentially increasing false sharing.

For example, scanning a contiguous array benefits from retrieving adjacent elements together. A pointer-chasing workload with random accesses may fetch many bytes that it never uses.

The chosen line size balances locality, transfer efficiency, metadata overhead, and coherence costs.

## 11. Inspecting cache lines on Linux

Linux exposes cache geometry through sysfs.

For example:

```bash
cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
```

On many modern x86 systems:

```text
64
```

Other useful properties include:

```bash
cat /sys/devices/system/cpu/cpu0/cache/index0/size
cat /sys/devices/system/cpu/cpu0/cache/index0/ways_of_associativity
cat /sys/devices/system/cpu/cpu0/cache/index0/number_of_sets
```

The `index0` path commonly describes the L1 data cache, but cache index numbering should be checked using the corresponding `level` and `type` attributes.

For a quick overview:

```bash
lscpu -C
```

For diagnosing cache-line contention on supported Linux systems:

```bash
perf c2c record -- ./application
perf c2c report
```

`perf c2c` is designed to help identify cache-to-cache contention, including true and false sharing.

## Key takeaways

- A cache line is the fundamental block used to store and transfer cached memory data.
- Modern x86 processors commonly use 64-byte cache lines.
- Accessing four bytes can bring 64 bytes into a cache.
- Cache lines exploit spatial locality and make sequential access efficient.
- Caches store metadata such as tags and coherence states alongside line data.
- Cache coherence typically operates on whole lines, not individual variables.
- Alignment, false sharing, and cache-line utilization can strongly affect multicore performance.
