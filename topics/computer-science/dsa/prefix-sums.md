# Prefix sums

Precompute cumulative sums so any range-sum query is $O(1)$.
Construction takes $O(n)$ time and $O(n)$ space.

## Construction

Allocate an array one element larger than the input. The leading zero
avoids a boundary check when the range starts at index 0:

```java
int[] buildPrefix(int[] nums) {
    int[] prefix = new int[nums.length + 1];

    for (int i = 0; i < nums.length; i++) {
        prefix[i + 1] = prefix[i] + nums[i];
    }

    return prefix;
}

// nums:   [2, 4, 1, 5, 3]
// prefix: [0, 2, 6, 7, 12, 15]
```

## Range query

Sum of elements from index L to R (0-based, inclusive):

$$\text{RangeSum}(L, R) = \text{prefix}[R + 1] - \text{prefix}[L]$$

Example — sum of indices 1..3 (values 4, 1, 5):

$$\text{prefix}[4] - \text{prefix}[1] = 12 - 2 = 10$$

## Pitfalls

**Integer overflow.** Cumulative sums grow fast. Use `long[]` if the
total could exceed $2^{31} - 1$.

**Static data only.** Prefix sums assume the array does not change. If
elements are updated between queries, the entire prefix array must be
rebuilt in $O(n)$. For dynamic updates, use a Fenwick tree or segment
tree instead.

## Related

- [Arrays](arrays.md) - Underlying data structure
- [Sliding window](sliding-window.md) - Alternative for contiguous ranges

---

Return to [Data structures and algorithms](_index.md)
