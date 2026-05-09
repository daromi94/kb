# Arena

An Arena controls the lifecycle of off-heap memory segments. It
provides temporal safety — accessing a segment after its arena is
closed throws IllegalStateException, preventing use-after-free
bugs.

## Arena types

| Type     | Thread access | Deallocation             |
|----------|---------------|--------------------------|
| Confined | Owner only    | Explicit `close()`       |
| Shared   | Any thread    | Explicit `close()`       |
| Auto     | Any thread    | GC-managed               |
| Global   | Any thread    | Never (process lifetime) |

**Confined** arenas (`Arena.ofConfined()`) give bounded, deterministic
lifetime. Only the thread that created the arena can access its
segments. Use try-with-resources to ensure prompt deallocation:

```java
try (Arena arena = Arena.ofConfined()) {
    MemorySegment seg = arena.allocateFrom("hello");
    // use seg within this block
} // off-heap memory freed here
```

**Shared** arenas (`Arena.ofShared()`) allow multiple threads to
access the same segments. Deallocation is still explicit via
`close()`.

**Auto** arenas (`Arena.ofAuto()`) delegate cleanup to the garbage
collector. Calling `close()` throws UnsupportedOperationException.
Useful when lifecycle tracking is impractical, but deallocation
timing is non-deterministic.

**Global** arena (`Arena.global()`) allocates memory that lives for
the entire process. Calling `close()` throws
UnsupportedOperationException.

## Temporal safety

A closed arena invalidates all its segments. Any subsequent access
throws IllegalStateException:

```java
MemorySegment seg;
try (Arena arena = Arena.ofConfined()) {
    seg = arena.allocateFrom("data");
}

// IllegalStateException: Already closed
seg.get(ValueLayout.JAVA_BYTE, 0);
```

This pairs with spatial bounds checking on MemorySegment to give
two-dimensional safety: spatial (in-bounds) and temporal (still
alive).

## Allocation methods

`Arena` implements SegmentAllocator, providing several allocation
methods:

- `allocate(byteSize, alignment)` — raw bytes with explicit
  alignment
- `allocateFrom(String)` — converts to a null-terminated UTF-8 C
  string

---

Return to [Native interop](_index.md)
