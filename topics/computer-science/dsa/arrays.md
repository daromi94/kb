# Arrays

An array stores a fixed number of same-typed elements in contiguous memory.
Any element's address is computed from the base address and element size,
so random access is $O(1)$.

## Memory layout in Java

Arrays are heap-allocated objects. A primitive array like `int[]` stores
values directly in contiguous memory. An object array like `String[]` stores
contiguous references — the objects themselves are scattered across the
heap. This distinction matters for cache locality: primitive arrays benefit
from sequential prefetching while object arrays suffer cache misses on every
dereference.

## Complexity

| Operation                     | Time       | Note                    |
|-------------------------------|------------|-------------------------|
| Access by index               | $O(1)$     | Address arithmetic      |
| Search (unsorted)             | $O(n)$     | Linear scan             |
| Search (sorted)               | $O(\lg n)$ | Binary search           |
| Insert/delete at end          | $O(1)$     | If tracking active size |
| Insert/delete at start/middle | $O(n)$     | Shift required          |
| Space                         | $O(n)$     | Fixed allocation        |

## Common patterns

**Frequency counting.** Use a small array to count occurrences — e.g.,
`new int[26]` for lowercase letters. Faster than a HashMap due to no
hashing or boxing overhead.

**Two pointers and sliding window.** Arrays pair naturally with algorithms
that advance left/right pointers over a contiguous range.

**Memoization.** 1D or 2D arrays are the standard DP cache. Much faster
than map-based state caching.

**Underlying storage.** Arrays back ArrayList, PriorityQueue (binary heap),
StringBuilder, and hash tables.

## Limitations

**Fixed size.** A Java array cannot grow after creation. Resizing requires
allocating a new array and copying all elements — $O(n)$.

**Costly mid-sequence mutation.** Inserting or deleting anywhere except the
end shifts all subsequent elements, making arrays a poor fit for queues or
frequent middle insertions.

## Pitfalls

**Primitives vs. wrappers.** Prefer `int[]` over `Integer[]`. Primitive
arrays store values contiguously for cache-friendly access; wrapper arrays
store scattered references.

**Off-by-one errors.** Check loop boundaries carefully (`< n` vs `<= n`)
and remember 0-based indexing.

**Default values.** Java zero-initializes arrays: `0` for numeric types,
`false` for booleans, `null` for object references. Forgetting the `null`
default on object arrays leads to NullPointerException.

**Filling multidimensional arrays.** `Arrays.fill(arr, value)` works on 1D
arrays only. For 2D, loop through each row:

```java
void fill2D(int[][] arr, int value) {
    for (int[] row : arr) {
        Arrays.fill(row, value);
    }
}
```

## Related

- [Grid flattening](grid-flattening.md) - 2D-to-1D conversion
- [Circular indexing](circular-indexing.md) - Modulo wrap-around
- [Two pointers](two-pointers.md) - Dual-index traversal
- [Sliding window](sliding-window.md) - Incremental subarray scan
- [Prefix sums](prefix-sums.md) - Cumulative range queries

---

Return to [Data structures and algorithms](_index.md)
