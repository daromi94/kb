# Circular indexing

Treat a fixed-size array as a closed loop: stepping past the last index
wraps to 0, stepping backward from 0 wraps to the end. This enables
data structures that continuously consume and release data without
allocating memory or shifting elements.

## Modulo arithmetic

```
forward:  (index + k) % N
backward: (index - k % N + N) % N
```

The backward formula adds N before the final `%` because Java's `%`
returns negative remainders for negative dividends (`-1 % 5` is `-1`,
not `4`).

Example — index 1, move back 3 in array of size 5:

$$(1 - 3 \bmod 5 + 5) \bmod 5 = (1 - 3 + 5) \bmod 5 = 3$$

## Power-of-two optimization

Modulo division is one of the slower arithmetic instructions. When N is
a power of two, N - 1 is a bitmask of all 1s, so modulo can be
replaced with bitwise AND:

```
(index + k) & (N - 1)
```

This is how ring buffers and the LMAX Disruptor achieve high-throughput
wrap-around.

## Ring buffer

A ring buffer uses two circularly-advancing pointers on a fixed array:

```
+---+---+---+---+---+---+---+---+
|   |   | x | x | x |   |   |   |
+---+---+---+---+---+---+---+---+
          ^           ^
         tail        head
```

**Head** — where the next write goes. **Tail** — the oldest unread
element. Both advance forward with circular indexing. As long as head
does not lap tail (buffer full), enqueue and dequeue are both $O(1)$ with
no allocation and no shifting.

## Related

- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
