# Binary search

**Binary search is an algorithm for finding a target in a sorted search space by repeatedly eliminating half of the remaining possibilities.**

Its central idea is simple:

> Instead of examining every element, use information about the ordering to determine which part of the search space cannot contain the answer.

Binary search is one of the most important algorithms in computer science because it introduces several foundational concepts: **divide and conquer, invariants, logarithmic complexity, and reasoning about search spaces.**

## 1. The problem

Consider a sorted array containing 16 elements:

```text
Index:   0   1   2   3   4   5   6   7
Value:   2   5   8  12  16  21  25  29

Index:   8   9  10  11  12  13  14  15
Value:  33  37  42  46  51  57  63  70
```

The objective is to find the index of `42`.

### Linear search

A straightforward approach examines every element until the target is found.

```text
FUNCTION linearSearch(A, target):
    FOR i FROM 0 TO length(A) - 1:
        IF A[i] == target:
            RETURN i

    RETURN -1
```

In the worst case, every element must be inspected.

For an array of `n` elements:

- **Time complexity:** `O(n)`
- **Space complexity:** `O(1)`

A million elements could require a million comparisons.

### Binary search

Because the array is sorted, comparing the target with the middle element reveals which half can be discarded.

```text
Sorted array
      |
      v
Check interval <--- Repeat -------------------------------+
      |                                                   |
      +-- Empty --> Return -1                             |
      |                                                   |
      v                                                   |
Examine middle                                            |
      |                                                   |
      +-- Target found ----> Return index                 |
      |                                                   |
      +-- Target smaller --> Search left -----------------+
      |                                                   |
      +-- Target larger ---> Search right ----------------+
```

The algorithm does not need to inspect the discarded half.

This is the critical optimization.

## 2. How binary search works

At each iteration, the algorithm maintains two boundaries:

- **`low`:** first index of the remaining search interval.
- **`high`:** last index of the remaining search interval.

The middle index is:

```text
mid = floor((low + high) / 2)
```

There are three possible outcomes:

| Comparison         | Action                                  |
| ------------------ | --------------------------------------- |
| `A[mid] == target` | Target found                            |
| `A[mid] < target`  | Discard the left half, including `mid`  |
| `A[mid] > target`  | Discard the right half, including `mid` |

**Every unsuccessful comparison makes the search space smaller.**

## 3. The algorithm

The classical implementation uses an inclusive search interval `[low, high]`.

```text
FUNCTION binarySearch(A, target):
    low = 0
    high = length(A) - 1

    WHILE low <= high:
        mid = low + (high - low) // 2

        IF A[mid] == target:
            RETURN mid

        ELSE IF A[mid] < target:
            low = mid + 1

        ELSE:
            high = mid - 1

    RETURN -1
```

The calculation:

```text
mid = low + (high - low) // 2
```

is preferred over:

```text
mid = (low + high) // 2
```

because adding `low + high` can overflow in languages using fixed-width integers.

### Why `mid + 1` and `mid - 1`?

Suppose:

```text
A[mid] < target
```

Since the array is sorted:

```text
All elements at indices <= mid
are smaller than target.
```

Therefore, none of those elements can contain the target.

The new lower boundary must be:

```text
low = mid + 1
```

Using `low = mid` would retain an index already proven invalid and could cause an infinite loop.

## 4. Correctness: the loop invariant

Binary search is particularly useful for understanding **loop invariants**.

**A loop invariant is a property that remains true before and after every iteration.**

For binary search:

> **If the target exists in the array and has not been found, at least one occurrence is inside the interval `[low, high]`.**

The proof has three parts.

### Initialization

Initially:

```text
low = 0
high = n - 1
```

The interval contains the entire array.

Therefore, if the target exists, it must lie inside the search interval.

The invariant holds.

### Maintenance

Assume the invariant holds at the beginning of an iteration.

Consider:

```text
A[mid] < target
```

Because the array is sorted:

```text
A[0] <= ... <= A[mid] < target
```

All positions up to `mid` can safely be discarded.

After:

```text
low = mid + 1
```

the invariant still holds.

The same reasoning applies symmetrically when `A[mid] > target`.

### Termination

Two outcomes are possible:

1. The target is found, and its index is returned.
2. The interval becomes empty (`low > high`).

In the second case, the invariant implies that the target cannot exist in the array.

Therefore, returning `-1` is correct.

**There is also a termination argument: each unsuccessful iteration strictly reduces the number of candidate elements. Consequently, the loop cannot continue forever.**

**The important distinction:** an invariant proves that the search does not discard a valid answer, while shrinking the interval proves that the algorithm eventually terminates.

## 5. Why binary search is O(log n)

Let `n` represent the number of elements.

Each iteration approximately halves the remaining search space.

```text
Initial candidates:     32
                         |
                         v
After 1 iteration:      16
                         |
                         v
After 2 iterations:      8
                         |
                         v
After 3 iterations:      4
                         |
                         v
After 4 iterations:      2
                         |
                         v
After 5 iterations:      1
```

After `k` iterations, the remaining number of candidates is approximately:

```text
n / 2^k
```

The process continues until only one candidate remains.

```text
n / 2^k = 1
```

Rearranging:

```text
2^k = n
```

Taking logarithms:

```text
k = log2(n)
```

Therefore:

```text
T(n) = O(log n)
```

### Comparison with linear search

Linear search versus binary search as array size increases.

| Elements      | Linear search (worst case) | Binary search (worst case) |
| ------------- | -------------------------- | -------------------------- |
| 100           | 100                        | 7                          |
| 1,000         | 1,000                      | 10                         |
| 1,000,000     | 1,000,000                  | 20                         |
| 1,000,000,000 | 1,000,000,000              | 30                         |

Binary search scales remarkably well: doubling the size of the input adds at most approximately one additional iteration.

Its space complexity is `O(1)` when implemented iteratively, because only a few variables are maintained.

## 6. The deeper idea: binary search on predicates

Binary search is not fundamentally about searching arrays.

It is about finding a **boundary in an ordered search space**.

Consider a predicate that transitions from false to true:

```text
Index:      0  1  2  3  4  5  6  7
Predicate:  F  F  F  F  T  T  T  T
                        ^
                    First true
```

The objective is to find the first index where the predicate becomes true.

This works because the predicate is _monotonic_: once it becomes true, it remains true.

A general-purpose binary search can find that boundary.

```text
FUNCTION firstTrue(n, predicate):
    low = 0
    high = n

    WHILE low < high:
        mid = low + (high - low) // 2

        IF predicate(mid):
            high = mid
        ELSE:
            low = mid + 1

    RETURN low
```

Here, the search uses the half-open interval `[low, high)`. The value `n` acts as the result when no index satisfies the predicate, so the predicate is never evaluated at `n`.

### Example: lower bound

Given:

```text
A = [2, 4, 4, 4, 7, 9]
target = 4
```

Ordinary binary search might return index `1`, `2`, or `3`.

But suppose the objective is to find the **first element greater than or equal to 4**.

Define:

```text
predicate(i) = A[i] >= 4
```

Then:

```text
Index:       0  1  2  3  4  5
Value:       2  4  4  4  7  9
Predicate:   F  T  T  T  T  T
                ^
              Answer
```

The answer is index `1`.

This operation is known as `lower_bound`.

It is useful for database indexes, insertion positions in sorted collections, range queries, and many other algorithms.

## 7. When binary search is appropriate

The search space must have some structure that allows a comparison or predicate evaluation to eliminate a substantial portion of the remaining possibilities.

| Situation                                    | Appropriate?      | Reason                                     |
| -------------------------------------------- | ----------------- | ------------------------------------------ |
| Sorted array                                 | Yes               | Ordering permits eliminating half          |
| Unsorted array                               | No, not directly  | Comparison gives no useful direction       |
| First value satisfying a monotonic condition | Yes               | There is a searchable boundary             |
| Sorted linked list                           | Usually not ideal | Finding the middle is expensive            |
| B-tree index                                 | Related technique | Uses sorted keys to narrow the search      |
| Finding a minimum feasible capacity          | Often yes         | Feasibility may form a monotonic predicate |

A crucial performance detail is that the `O(log n)` bound assumes comparisons and middle-element access take `O(1)` time.

For linked lists, accessing the middle requires traversal, removing much of the advantage.

For expensive predicates, total time is:

```text
O(log n * C)
```

where `C` is the cost of evaluating the predicate.

## 8. Common pitfalls

Binary search has a short implementation but is notorious for boundary errors.

- **Incorrect interval convention:** Mixing inclusive `[low, high]` and half-open `[low, high)` implementations.
- **Infinite loops:** Updating `low = mid` when `mid` has already been eliminated.
- **Off-by-one errors:** Using `<` instead of `<=` for an inclusive search interval.
- **Duplicates:** Assuming ordinary binary search always finds the first occurrence.
- **Invalid assumptions:** Applying binary search to a predicate that is not monotonic.

**A useful engineering practice is to state the interval convention and loop invariant before writing the algorithm.**

The central lesson is that **binary search transforms ordering information into the ability to discard possibilities**. Its power comes not from examining elements faster, but from avoiding examining most elements at all.
