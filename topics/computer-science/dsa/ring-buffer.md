# Ring buffer

A **ring buffer** is a fixed-capacity data structure that stores elements in a circular arrangement, allowing efficient insertion and removal without shifting elements in memory.

It is commonly used in operating systems, networking, concurrency, logging, and high-performance data pipelines.

The central idea:

> Reuse a fixed region of memory by wrapping read and write positions back to the beginning when they reach the end.

A ring buffer typically implements a **FIFO (First In, First Out)** queue with constant-time operations.

## 1. The problem: moving data through a queue

Consider a producer generating data and a consumer processing it.

```text
     Producer
        |
        v
+---------------+
| Queue         |
+---------------+
        |
        v
     Consumer
```

The producer and consumer may operate at different speeds.

For example:

- A network interface receives packets.
- An application processes those packets.
- Packets arriving faster than they can be processed need temporary storage.

A queue solves this problem by decoupling production from consumption.

However, implementing a queue using a simple array can introduce unnecessary work.

Consider:

```text
Capacity = 5

Index:    0   1   2   3   4
        +---+---+---+---+---+
        | A | B | C | D | E |
        +---+---+---+---+---+
          ^
          |
         Read
```

After consuming `A`, one possible implementation shifts all remaining elements left.

```text
Before:

        +---+---+---+---+---+
        | A | B | C | D | E |
        +---+---+---+---+---+

After:

        +---+---+---+---+---+
        | B | C | D | E |   |
        +---+---+---+---+---+
```

Shifting elements requires `O(n)` work.

A ring buffer avoids this entirely.

Instead of moving elements, **move the indices**.

## 2. The basic architecture

A ring buffer consists of three main components:

- **`buffer`:** Fixed-size storage for elements.
- **`head`:** Position of the next element to read.
- **`tail`:** Position where the next element will be written.

A convenient implementation also maintains `size`, the number of elements currently stored.

```text
RING BUFFER

Capacity = 5

Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: | A | B | C |   |   |
        +---+---+---+---+---+
          ^           ^
          |           |
         head        tail

head = 0
tail = 3
size = 3
```

The next read removes `A`.

The next write inserts an element at index `3`.

Unlike an ordinary linear queue, the storage positions are reusable.

### The circular property

Suppose the tail reaches the final position:

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: | A | B | C | D |   |
        +---+---+---+---+---+
                          ^
                          |
                         tail
```

After writing at index `4`, the next tail position becomes `0`.

This is implemented using modulo arithmetic:

```text
nextIndex = (currentIndex + 1) MOD capacity
```

For capacity `5`:

```text
0 -> 1 -> 2 -> 3 -> 4
^                   |
|                   |
+-------------------+
```

Mathematically:

```text
next(0) = (0 + 1) MOD 5 = 1
next(1) = (1 + 1) MOD 5 = 2
next(2) = (2 + 1) MOD 5 = 3
next(3) = (3 + 1) MOD 5 = 4
next(4) = (4 + 1) MOD 5 = 0
```

This wrapping behavior gives the ring buffer its name.

**Importantly, the underlying memory is not circular. It remains an ordinary contiguous array. Only the indexing logic is circular.**

## 3. Step-by-step example

Consider a ring buffer of capacity `5`.

### Initial state

The buffer starts empty.

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: |   |   |   |   |   |
        +---+---+---+---+---+

head = 0
tail = 0
size = 0
```

### Operation 1: enqueue A, B, C

Insert three elements.

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: | A | B | C |   |   |
        +---+---+---+---+---+
          ^           ^
          |           |
         head        tail

head = 0
tail = 3
size = 3
```

### Operation 2: dequeue twice

Remove `A` and `B`.

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: |   |   | C |   |   |
        +---+---+---+---+---+
                  ^   ^
                  |   |
                 head |
                     tail

head = 2
tail = 3
size = 1
```

Notice that `C` remains at index `2`.

No elements were shifted.

Only the `head` index changed.

### Operation 3: enqueue D, E

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: |   |   | C | D | E |
        +---+---+---+---+---+
          ^       ^
          |       |
         tail    head

head = 2
tail = 0
size = 3
```

The tail has wrapped back to index `0`.

### Operation 4: enqueue F

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: | F |   | C | D | E |
        +---+---+---+---+---+
              ^   ^
              |   |
             tail |
                 head

head = 2
tail = 1
size = 4
```

Observe the physical layout:

```text
Physical order:

Index:    0   1   2   3   4
          F   -   C   D   E
```

But the logical FIFO order is:

```text
Logical order:

C -> D -> E -> F
```

**Physical array order and logical queue order are no longer identical.**

This is the most important distinction in understanding a ring buffer.

### Operation 5: enqueue G

```text
Index:    0   1   2   3   4
        +---+---+---+---+---+
Buffer: | F | G | C | D | E |
        +---+---+---+---+---+
                  ^
                  |
              head, tail

head = 2
tail = 2
size = 5
```

The buffer is full.

Notice something interesting:

```text
Empty buffer:
    head == tail

Full buffer:
    head == tail
```

How can the implementation distinguish these states?

That leads to an important design decision.

## 4. Distinguishing empty and full buffers

There are several common approaches.

### Approach A: track the number of elements

Maintain a `size` counter.

```text
EMPTY:
    size == 0

FULL:
    size == capacity
```

This is simple and allows the buffer to use every available slot.

However, the counter introduces additional synchronization considerations when multiple threads access the buffer.

### Approach B: reserve one unused slot

Another approach deliberately keeps one slot empty.

```text
EMPTY:
    head == tail

FULL:
    (tail + 1) MOD capacity == head
```

For example:

```text
Physical capacity = 5

        +---+---+---+---+---+
        | A | B | C | D |   |
        +---+---+---+---+---+
          ^               ^
          |               |
         head            tail

Stored elements = 4
Usable capacity = 4
```

This simplifies some implementations but sacrifices one storage slot.

### Approach C: monotonically increasing counters

A more sophisticated approach uses read and write counters that continually increase.

```text
readSequence  = number of consumed elements
writeSequence = number of published elements
```

Then:

```text
EMPTY:
    writeSequence == readSequence

FULL:
    writeSequence - readSequence == capacity
```

Physical positions are computed using modulo:

```text
readIndex  = readSequence MOD capacity
writeIndex = writeSequence MOD capacity
```

This separates the _logical progress of the queue_ from the _physical memory location_.

It is especially useful for concurrent ring buffers.

The counters must be sufficiently wide, and their wraparound behavior must be accounted for in a production implementation.

## 5. Ring buffer implementation

A straightforward implementation maintains `head`, `tail`, and `size`.

### Initialization

```text
FUNCTION createRingBuffer(capacity):
    REQUIRE capacity > 0

    ring.buffer = new array[capacity]
    ring.capacity = capacity
    ring.head = 0
    ring.tail = 0
    ring.size = 0

    RETURN ring
```

### Enqueue

```text
FUNCTION enqueue(ring, value):
    IF ring.size == ring.capacity:
        RETURN FULL

    ring.buffer[ring.tail] = value

    ring.tail = (ring.tail + 1) MOD ring.capacity

    ring.size = ring.size + 1

    RETURN SUCCESS
```

### Dequeue

```text
FUNCTION dequeue(ring):
    IF ring.size == 0:
        RETURN EMPTY

    value = ring.buffer[ring.head]

    ring.head = (ring.head + 1) MOD ring.capacity

    ring.size = ring.size - 1

    RETURN value
```

**This pseudocode describes a sequential implementation. Concurrent producers and consumers require synchronization.**

### Complexity

| Operation        | Time complexity |
| ---------------- | --------------- |
| Enqueue          | `O(1)`          |
| Dequeue          | `O(1)`          |
| Peek             | `O(1)`          |
| Check empty/full | `O(1)`          |
| Initialization   | `O(n)`          |

Storage complexity is `O(n)`, where `n` is the capacity.

No allocation is required per operation after initialization, assuming the elements fit in preallocated storage.

## 6. Why ring buffers are important for performance

Ring buffers have several properties that make them attractive in systems engineering.

### A. No shifting of elements

A ring buffer only updates indices.

```text
Traditional shifting queue:

    Remove first element
             |
             v
  Shift remaining elements
             |
             v
            O(n)


Ring buffer:

    Remove first element
             |
             v
        Advance head
             |
             v
            O(1)
```

### B. Predictable memory usage

The maximum storage requirement is determined during initialization.

A fixed-capacity ring buffer does not grow automatically.

This is valuable in environments where allocations must be minimized, such as real-time processing.

### C. Good spatial locality

Elements are stored in a contiguous array.

```text
Memory:

+-------+-------+-------+-------+-------+
| Slot0 | Slot1 | Slot2 | Slot3 | Slot4 |
+-------+-------+-------+-------+-------+
```

Sequential traversal generally benefits from CPU cache locality and hardware prefetching.

There are important qualifications:

- The buffer may be split into two physical regions when it wraps.
- Elements stored indirectly as pointers may require additional memory accesses.
- Cache-line contention can still degrade concurrent performance.

Contiguous storage provides useful locality properties, but does not guarantee optimal performance.

### D. Bounded memory

Because the capacity is fixed, queue growth cannot consume unlimited memory.

However, a full buffer requires an explicit policy.

Possible policies include:

- Reject the incoming element.
- Block the producer until space becomes available.
- Overwrite the oldest element.
- Drop the incoming element.

Each policy represents a different engineering tradeoff.

## 7. Ring buffers and concurrency

One of the most important applications is communication between producer and consumer threads.

```text
        Thread A
        Producer
           |
           | enqueue
           v
+---------------------+
| Ring Buffer         |
+---------------------+
           |
           | dequeue
           v
        Thread B
        Consumer
```

The ring buffer acts as an intermediary.

Both threads can make progress independently, subject to available data and free capacity.

However, **a ring buffer is not automatically thread-safe**.

Concurrency introduces additional concerns:

- Visibility of writes between CPU cores.
- Atomicity of indices and counters.
- Memory ordering.
- False sharing and cache-line contention.
- Coordination between multiple producers or consumers.

### Single producer, single consumer (SPSC)

The simplest concurrent design has one producer and one consumer.

```text
    Producer Core                     Consumer Core
   +-------------+                   +-------------+
   |             |                   |             |
   | Owns tail   |                   | Owns head   |
   |             |                   |             |
   +------+------+                   +------+------+
          |                                 ^
          |                                 |
          v                                 |
+---------+---------------------------------+---------+
|                     Ring Buffer                     |
|                                                     |
|              [ A ][ B ][ C ][   ][   ]              |
|                                                     |
+-----------------------------------------------------+
```

The producer exclusively advances the write position.

The consumer exclusively advances the read position.

This ownership separation can eliminate the need for a mutex, provided the implementation uses correct atomic operations and memory ordering.

### SPSC with sequence counters

A useful design maintains:

```text
readSequence
writeSequence
```

Both are atomic counters.

The producer owns updates to `writeSequence`, while the consumer owns updates to `readSequence`.

**The producer publishes a slot only after the element has been written.**

```text
PRODUCER:

FUNCTION tryWrite(value):
    w = writeSequence.load(RELAXED)
    r = readSequence.load(ACQUIRE)

    IF w - r == capacity:
        RETURN FULL

    buffer[w MOD capacity] = value

    writeSequence.store(w + 1, RELEASE)

    RETURN SUCCESS
```

The consumer checks whether an element has been published before reading it.

```text
CONSUMER:

FUNCTION tryRead():
    r = readSequence.load(RELAXED)
    w = writeSequence.load(ACQUIRE)

    IF r == w:
        RETURN EMPTY

    value = buffer[r MOD capacity]

    readSequence.store(r + 1, RELEASE)

    RETURN value
```

This is conceptual SPSC pseudocode. It assumes valid atomic sequence arithmetic, suitable slot storage, and that no other thread modifies the same endpoint.

The acquire/release operations establish the necessary ordering.

For example:

```text
      Producer                                  Consumer

 Write buffer[slot]
         |
         v
Store writeSequence
      RELEASE
         |
         |  Synchronizes with
         |  matching ACQUIRE
         +-------------------------------> Load writeSequence
                                                ACQUIRE
                                                   |
                                                   v
                                           Read buffer[slot]
```

**The consumer must not observe a newly published write position without also observing the element written before publication.**

**Similarly, the consumer releases a slot only after reading it, and the producer uses acquire semantics before reusing that slot.**

### Why multiple producers are harder

Consider two producers accessing the same write position.

```text
  Producer A                      Producer B
      |                               |
      v                               v
Read tail = 3                   Read tail = 3
      |                               |
      v                               v
 Write slot 3                    Write slot 3
```

Without coordination, both producers might write to the same slot.

A multi-producer design requires a safe way to reserve unique slots.

Common approaches include:

- Locks.
- Atomic compare-and-swap operations.
- Per-slot sequence numbers.

An MPMC (Multi-Producer, Multi-Consumer) ring buffer is significantly more complicated than an SPSC ring buffer.

A particularly important distinction is between **reserving a slot** and **publishing a completed write**. Consumers must not read slots that have been reserved but not initialized.

## 8. Backpressure: what happens when the buffer is full?

A ring buffer cannot absorb an unlimited difference between producer and consumer speeds.

Suppose:

```text
Producer rate = 1,000 items/sec

Consumer rate =   700 items/sec

Net growth    =   300 items/sec
```

If the buffer can hold 3,000 items and starts empty, it fills in approximately 10 seconds, assuming constant rates.

```text
        Producer
         1000/s
           |
           v
+---------------------+
| Ring Buffer         |
|                     |
| Occupancy increases |
|                     |
+---------------------+
           |
           v
        Consumer
         700/s
```

**A ring buffer smooths temporary bursts.**

**It does not solve sustained overload.**

This distinction is important in networking and distributed systems.

### Common full-buffer policies

**Blocking**

The producer waits until the consumer frees space.

This creates backpressure.

**Dropping**

The producer discards the new item when the buffer is full.

This is useful when dropping is preferable to blocking.

**Overwriting**

The newest item replaces the oldest item.

This is appropriate for some telemetry or sampling systems where recent observations matter more than historical completeness.

**An overwrite policy needs its own safe synchronization protocol in a concurrent implementation; simply advancing the consumer's read position from a producer can introduce races.**

## 9. Common applications

### Network packet processing

Network interfaces and networking software commonly use circular descriptor rings to manage packet buffers.

```text
Network Interface
        |
        v
RX Descriptor Ring
        |
        v
 Driver / Kernel
        |
        v
Packet Processing
```

A descriptor may contain information about a packet buffer rather than the packet payload itself.

The ring allows efficient reuse of descriptor slots.

### Audio processing

Audio systems use circular buffers to transfer samples between threads or devices operating at different rates.

```text
 Audio Capture
       |
       v
Circular Buffer
       |
       v
 Audio Playback
```

Insufficient buffering may cause underruns, while excessive buffering increases latency.

### Logging systems

A background logger can consume events that application threads publish to a ring buffer.

```text
Application Threads
         |
         v
    Ring Buffer
         |
         v
   Logging Thread
         |
         v
      Storage
```

This can move some logging work off latency-sensitive application threads, although the queue still needs an overload policy.

### Streaming and messaging

Ring buffers are useful in bounded, in-memory event pipelines where predictable allocations and efficient producer-consumer communication matter.

## 10. Engineering tradeoffs

| Property                 | Ring buffer                            |
| ------------------------ | -------------------------------------- |
| Storage                  | Fixed capacity                         |
| Enqueue/dequeue          | `O(1)`                                 |
| Allocation per operation | Usually none                           |
| Memory locality          | Generally good                         |
| Dynamic growth           | Not automatic                          |
| Concurrent access        | Requires careful design                |
| Overflow handling        | Must be defined                        |
| Best suited for          | Bounded queues and streaming workloads |

A ring buffer is not necessarily superior to every queue implementation.

For example, a linked-list queue can grow dynamically, while a fixed-capacity ring buffer cannot.

A dynamically resized array queue can also provide amortized `O(1)` operations, but may incur occasional allocation and copying.

The appropriate design depends on capacity requirements, concurrency patterns, memory constraints, and latency objectives.

## Core takeaway

The fundamental idea behind a ring buffer is **separating logical queue progress from physical storage locations**.

```text
Logical queue:

A -> B -> C -> D -> E
        FIFO


Physical storage:

        +---+---+---+---+---+
        | D | E | A | B | C |
        +---+---+---+---+---+


Read/write indices determine logical order.
Modulo arithmetic determines physical location.
```

Three engineering principles make ring buffers valuable:

1. **Move metadata instead of data.** Advancing indices is cheaper than shifting elements.
2. **Reuse bounded storage.** Preallocation provides predictable memory consumption and avoids per-operation allocations.
3. **Separate ownership and publication.** In concurrent designs, safe coordination requires clear ownership of positions and correct memory ordering.

The most interesting extension is the relationship between ring buffers, CPU cache coherence, memory barriers, and lock-free algorithms: a simple circular array can become a highly efficient communication mechanism between threads or CPU cores.
