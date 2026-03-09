# Grid flattening

Store a grid with $R$ rows and $C$ columns in a 1D array of size
$R \times C$. One contiguous allocation replaces an array-of-arrays,
improving cache locality and reducing object overhead.

## Index conversion

Translate between `(row, col)` and a flat index:

```text
index = row * C + col
row   = index / C
col   = index % C
```

Example — 8x8 board, position $(2, 3)$:

$$2 \times 8 + 3 = 19 \quad \longrightarrow \quad 19 / 8 = 2,\; 19 \bmod 8 = 3$$

## Benefits

**Cache locality.** A single `int[]` is one contiguous block. The CPU
prefetcher pulls upcoming elements into cache automatically. An
`int[][]` scatters rows across the heap, causing misses on every row
transition.

**Less object overhead.** `int[1000][1000]` creates 1,001 objects (one
reference array + 1,000 row arrays). `int[1000000]` creates one.

**Simpler state.** A single integer index is cheaper to enqueue for BFS
than a two-element coordinate array.

**Required for 1D-indexed structures.** Union-Find on a grid needs a
flat parent array — flatten coordinates to map cells into it.

## Related

- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
