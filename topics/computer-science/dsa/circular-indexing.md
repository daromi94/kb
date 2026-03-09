# Circular indexing

Treat a fixed-size array as a loop: stepping past the last index wraps
to 0, stepping backward from 0 wraps to the end. This avoids shifting
elements or allocating new memory.

## Modulo arithmetic

Wrap any offset back into bounds with `%`:

```text
forward:  (index + k) % N
backward: (index - k % N + N) % N
```

The backward formula adds N before the final `%` because Java's `%`
is a remainder, not a true modulo — it returns negative values for
negative dividends (`-1 % 5` is `-1`, not `4`).

Example — index 1, move back 3 in array of size 5:

$$(1 - 3 \bmod 5 + 5) \bmod 5 = (1 - 3 + 5) \bmod 5 = 3$$

## Power-of-two optimization

When N is a power of two, replace `%` with bitwise AND — much faster:

```text
(index + k) & (N - 1)
```

N - 1 is a bitmask of all 1s, so the AND strips the high bits. This
is how the LMAX Disruptor and similar ring buffers achieve
high-throughput wrap-around.

## Ring buffer

Two circularly-advancing pointers on a fixed array give $O(1)$ enqueue
and dequeue with no allocation:

```text
+---+---+---+---+---+---+---+---+
|   |   | x | x | x |   |   |   |
+---+---+---+---+---+---+---+---+
          ^           ^
         tail        head
```

**Head** — next write position. **Tail** — oldest unread element. Both
advance forward. The buffer is full when head would lap tail.

## Limitations

Ring buffers have a fixed capacity set at creation. If the producer
can outpace the consumer indefinitely, a growable queue is a better
fit.

## Related

- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
