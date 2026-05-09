# MemorySegment

MemorySegment is the core abstraction in the Foreign Function &
Memory (FFM) API. It represents a contiguous region of memory with
built-in spatial safety — every access is bounds-checked at runtime.

## Spatial bounds

A MemorySegment tracks its size in bytes. Every read or write is
validated against these bounds. Accessing outside the segment throws
IndexOutOfBoundsException, preventing buffer overflows, segfaults,
and silent memory corruption that plague raw C pointers.

## Segment types

| Type   | Backing            | Created via                     |
|--------|--------------------|---------------------------------|
| Native | Off-heap OS memory | `Arena.allocate()`              |
| Heap   | On-heap Java array | `MemorySegment.ofArray(byte[])` |

Both types expose the same MemorySegment interface, so the same
code can operate on either without changes.

## Reading and writing with ValueLayout

Data access requires a ValueLayout, which defines the size, byte
alignment, and byte order (endianness) of the primitive type.

```java
import java.lang.foreign.Arena;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;

try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(16, 8);

    // Write a 32-bit int at offset 0 (bytes 0-3)
    segment.set(ValueLayout.JAVA_INT, 0, 42);

    // Write a 64-bit double at offset 8 (bytes 8-15)
    segment.set(ValueLayout.JAVA_DOUBLE, 8, 3.14159);

    // Read the int back
    int value = segment.get(ValueLayout.JAVA_INT, 0);
}
```

Offsets must satisfy the layout's alignment constraint. JAVA_DOUBLE
requires 8-byte alignment — writing it at an unaligned offset like
4 throws IllegalArgumentException. The allocation itself must also
request sufficient alignment (second argument to `allocate()`).

## Slicing

`asSlice(offset, newSize)` creates a new MemorySegment view over a
sub-region of the original. The slice shares the parent's temporal
bounds (lifetime) but enforces narrower spatial bounds. This allows
passing restricted memory ranges to native functions without risk of
out-of-bounds access.

---

Return to [Native interop](_index.md)
