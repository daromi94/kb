# Grid flattening

Replace a Java `int[][]` with a single `int[]` of size `R * C`. A 2D
array is actually an array of references to independent row arrays
scattered across the heap. Flattening collapses this into one contiguous
block.

## Index conversion

```
index = row * C + col
row   = index / C
col   = index % C
```

On an 8x8 board, position $(2, 3)$ maps to index
$2 \times 8 + 3 = 19$. Reversing: $19 / 8 = 2$ (row),
$19 \bmod 8 = 3$ (col).

## Why flatten

**Cache locality.** A 1D array is a single contiguous allocation. The
CPU prefetcher pulls upcoming elements into L1/L2 cache automatically.
A 2D array scatters rows across the heap, causing cache misses on every
row transition.

**Memory overhead.** Every Java object carries a header (12-16 bytes).
An `int[1000][1000]` creates 1,001 objects — one reference array plus
1,000 row arrays. An `int[1000000]` creates one.

**Simplified state.** A single integer index is cheaper to push into a
`Queue<Integer>` for BFS than a two-element array or custom point
object.

## Applications

Flattening is required for data structures that operate on a 1D parent
array, such as Union-Find on a grid. Flatten grid coordinates to map
them into the DSU array.

## Related

- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
