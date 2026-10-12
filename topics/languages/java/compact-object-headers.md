# Compact Object Headers

Compact Object Headers are a JVM optimization that reduces the memory required to store metadata for every Java object.

On a typical 64-bit HotSpot JVM, the object header shrinks from 12 bytes to 8 bytes, a reduction of approximately 33% in header size.

This optimization originated in OpenJDK Project Lilliput, whose goal is to reduce the memory footprint of Java objects.

The feature evolved through three releases:

- JDK 24: Experimental (JEP 450).
- JDK 25: Production-ready, but opt-in (JEP 519).
- JDK 27: Enabled by default (JEP 534)

The important insight is that Java objects consume memory beyond their actual fields, and that overhead becomes significant when millions of objects are allocated.

## 1. Understanding Java object layout

Consider a simple Java class:

```java
class Person {
    int age;
    int id;
}
```

A `Person` instance contains two integers, requiring 8 bytes of field data.

However, the JVM needs additional information about the object.

On a traditional 64-bit HotSpot JVM with compressed class pointers and 8-byte object alignment, the layout is:

```text
Person object
+--------------------------+
| Mark Word        8 bytes |
+--------------------------+
| Class Pointer    4 bytes |
+--------------------------+
| age              4 bytes |
+--------------------------+
| id               4 bytes |
+--------------------------+
| Padding          4 bytes |
+--------------------------+
| Total           24 bytes |
+--------------------------+
```

Only 8 of the 24 bytes contain application data.

The remaining 16 bytes represent JVM metadata and padding.

### What is the object header?

The traditional header contains two components.

**Mark Word (8 bytes)**

Stores runtime metadata associated with an object, including:

- Identity hash code, when computed.
- Locking state.
- Garbage collection age.
- Certain garbage collector states.

**Class Pointer (4 bytes)**

Identifies the JVM's internal class metadata (`Klass`) describing the object.

Conceptually:

```text
  Java Heap                 Metaspace

  +--------------------+
  | Person object      |
  |                    |
  | Mark Word          |
  |                    |
  | Class Pointer -----+----------+
  |                    |          |
  | age = 30           |          v
  | id = 100           |    +-----------------+
  +--------------------+    | Klass: Person   |
                            |-----------------|
                            | Type metadata   |
                            | Field layout    |
                            | Method metadata |
                            | ...             |
                            +-----------------+
```

The class pointer is an internal HotSpot pointer, not a Java `Class<?>` reference. It allows the JVM to determine the object's type and interpret its layout.

## 2. How Compact Object Headers work

The central optimization is surprisingly simple:

Instead of keeping the Mark Word and Class Pointer separate, HotSpot combines their information into one 64-bit word.

Traditional layout:

```text
+-----------------------+
| Mark Word     64 bits |
+-----------------------+
| Class Pointer 32 bits |
+-----------------------+

96 bits = 12 bytes
```

Compact layout:

```text
+------------------------+
| Compact Header 64 bits |
|                        |
| - Class information    |
| - Identity hash        |
| - Lock state           |
| - GC metadata          |
+------------------------+

64 bits = 8 bytes
```

How can the same information fit into fewer bits?

The traditional 64-bit Mark Word contains unused bits. Compact Object Headers reuse those bits to store a more compressed representation of the class pointer.

### Inside the 64-bit compact header

The bit layout is:

```text
Most significant                            Least significant
bit                                                       bit
63                                                          0
+---------+---------+----------+--------+----------+--------+
| Klass   | Hash    | Reserved | Age    | Self-fwd | Lock   |
| 22 bits | 31 bits | 4 bits   | 4 bits | 1 bit    | 2 bits |
+---------+---------+----------+--------+----------+--------+

<------------------------- 64 bits ------------------------->
```

| Field           | Bits | Purpose                                    |
| --------------- | ---- | ------------------------------------------ |
| Klass           | 22   | Encoded class metadata pointer             |
| Hash            | 31   | Identity hash code                         |
| Reserved        | 4    | Reserved for Project Valhalla              |
| Age             | 4    | Object age used by generational collectors |
| Self-forwarding | 1    | Special GC forwarding state                |
| Lock            | 2    | Object synchronization state               |

The traditional compressed class pointer uses 32 bits. Compact headers use a more specialized encoding that fits in 22 bits.

Crucially, the 31-bit identity hash code is preserved rather than reduced.

## 3. Memory savings: a concrete example

Consider the same `Person` class with two `int` fields.

```text
Traditional                  Compact
24 bytes per object          16 bytes per object

+------------------------+   +------------------------+
| Mark Word       8 B    |   | Header          8 B    |
+------------------------+   +------------------------+
| Class Pointer   4 B    |   | Fields          8 B    |
+------------------------+   +------------------------+
| Fields          8 B    |
+------------------------+
| Padding         4 B    |
+------------------------+

Object size reduction: 33.3%
```

For 10 million such objects, the idealized reduction in object storage is approximately 80 MB, without changing any Java application code.

### Why the savings are not always 4 bytes

Java objects are generally aligned to 8-byte boundaries in typical HotSpot configurations. This means reducing the header by 4 bytes can eliminate additional padding, or the alignment can absorb the savings.

| Object fields    | Traditional | Compact | Saved |
| ---------------- | ----------- | ------- | ----- |
| No fields        | 16 B        | 8 B     | 8 B   |
| One `int`        | 16 B        | 16 B    | 0 B   |
| Two `int` fields | 24 B        | 16 B    | 8 B   |

These are illustrative instance sizes with 8-byte alignment.

Therefore, actual heap savings depend on object sizes, field layouts, alignment, and the distribution of objects.

## 4. Why performance can improve

Compact Object Headers are primarily a memory optimization, but their performance benefits extend beyond memory consumption.

### A. Better CPU cache utilization

CPUs transfer memory into caches in units called cache lines, commonly 64 bytes.

Smaller objects allow more application data to fit in the same cache capacity.

```text
Traditional objects (24 bytes each)

64-byte cache line
+-----------------+-----------------+-----------+
| Object A        | Object B        | Remaining |
| 24 bytes        | 24 bytes        | 16 bytes  |
+-----------------+-----------------+-----------+

Compact objects (16 bytes each)

64-byte cache line
+-----------+-----------+-----------+-----------+
| Object A  | Object B  | Object C  | Object D  |
| 16 bytes  | 16 bytes  | 16 bytes  | 16 bytes  |
+-----------+-----------+-----------+-----------+
```

This is a simplified packing illustration, not a guarantee of how separate objects will be arranged in memory.

The consequences can include:

- Fewer cache misses.
- Less data transferred from DRAM.
- Improved effective memory bandwidth utilization.
- Better spatial locality when accessing related objects.

This is especially relevant to pointer-heavy structures such as trees, graphs, hash maps, and object-based query execution structures.

### B. Reduced garbage collection work

Garbage collectors operate on objects, not merely their application fields.

Smaller objects can reduce the live heap footprint, which can translate into lower memory pressure and less work during copying and compaction.

```text
                Smaller object headers
                         |
              +----------+----------+
              |                     |
              v                     v
       Smaller live heap     Better cache locality
              |                     |
              v                     v
       Less GC pressure      Fewer cache misses
              |                     |
              +----------+----------+
                         |
                         v
                 Potentially lower
                  CPU utilization
```

For example, benchmarks cited by the OpenJDK team reported a 22% heap reduction and 8% CPU reduction in one SPECjbb2015 configuration. Those are workload-specific measurements, not universal guarantees.

## 5. What about synchronization and garbage collection?

Shrinking an object header is more complicated than removing four bytes.

The JVM must still support `synchronized`, `System.identityHashCode()`, and garbage collection.

A particularly important difficulty is that the compact header contains class information that must remain available while the JVM performs these operations.

### Synchronization

Historically, some HotSpot locking implementations could replace the Mark Word with a pointer to lock-related information.

With compact headers, overwriting the entire word would also overwrite the encoded class pointer.

Consequently, lightweight locking primarily manipulates the lock-state bits while keeping the class information intact. Inflated monitors use external monitor structures and associated machinery.

```text
        Compact Object Header
        +-----------------------------+
        | Klass | Hash | ... | Lock   |
        +-----------------------------+
          ^                    ^
          |                    |
       Preserved           Lock state
       during              can change
       locking
```

### Garbage collection

Moving collectors sometimes need to record where an object has been relocated.

The compact-header design requires forwarding mechanisms that preserve or recover the object's class information. This is why the change required modifications across HotSpot's object representation, locking, and GC implementations, rather than merely changing a structure's size.

## 6. Compact Object Headers vs. Compressed OOPs

These are two different JVM optimizations.

Compressed Ordinary Object Pointers (Compressed OOPs) reduce the space required for references between Java objects, typically from 8 bytes to 4 bytes.

Compact Object Headers reduce the space required for the metadata stored inside each object.

```text
         Object A
  +---------------------+
  | Compact Header      | <--- Compact Object Headers
  |                     |
  | reference to B -----+-----+
  +---------------------+     |
                              |
           Compressed OOP ----+
                              |
                              v
                        Object B
                 +---------------------+
                 | Compact Header      |
                 |                     |
                 | Fields              |
                 +---------------------+
```

Compact Object Headers use a further-compressed class pointer in their metadata word. That is different from compressing ordinary Java object references.

Both optimizations improve memory efficiency, but they operate on different parts of an object's layout.

## 7. How to enable Compact Object Headers

The required flags depend on the Java version.

| JDK   | Configuration                                                   |
| ----- | --------------------------------------------------------------- |
| 24    | `-XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders` |
| 25–26 | `-XX:+UseCompactObjectHeaders`                                  |
| 27    | Enabled by default                                              |

With JDK 27, compact headers can still be disabled for comparison:

```bash
java -XX:-UseCompactObjectHeaders MyApplication
```

Check the setting:

```bash
java -XX:+PrintFlagsFinal -version | grep UseCompactObjectHeaders
```

On JDK 27, the default should show `true`.

## 8. When does this optimization matter most?

Compact Object Headers are particularly beneficial when the Java heap contains millions of small objects.

For example:

- In-memory caches containing small entries.
- Graphs, trees, and linked data structures.
- Large numbers of DTOs and domain objects.
- Query engines with object-heavy intermediate representations.
- Applications where GC pressure is driven by large object populations.

The benefits are generally smaller when memory is dominated by large primitive arrays, a few very large objects, or off-heap allocations.

A reasonable performance evaluation compares live heap occupancy, allocation rates, GC frequency, GC CPU time, throughput, and latency with the feature enabled and disabled.

## Key takeaway

Compact Object Headers illustrate an important JVM performance principle:

Reducing memory overhead can improve CPU performance even when the application performs exactly the same computations.

The optimization reduces object size, potentially improves cache locality and memory bandwidth efficiency, and can lower garbage collection costs.
