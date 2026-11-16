# Prefix sums

**Prefix sums are a technique for efficiently computing the sum of any contiguous range of elements in an array.**

The central idea is simple:

> Instead of repeatedly summing the same elements, precompute cumulative sums so that any range sum can be answered using two lookups and one subtraction.

Prefix sums introduce several important computer science concepts:

- **Precomputation:** Perform work once to make future operations faster.
- **Time-space tradeoffs:** Use additional memory to reduce computation.
- **Algebraic decomposition:** Transform an expensive operation into a simpler equivalent expression.
- **Range queries:** Efficiently answer questions about intervals of data.

## 1. The problem: range sum queries

Consider the following array:

```text
Index:   0   1   2   3   4   5   6
       +---+---+---+---+---+---+---+
A:     | 3 | 1 | 4 | 1 | 5 | 9 | 2 |
       +---+---+---+---+---+---+---+
```

Suppose the objective is to calculate the sum of elements between indices `2` and `5`, inclusive.

```text
Index:   0   1   2   3   4   5   6
       +---+---+---+---+---+---+---+
A:     | 3 | 1 | 4 | 1 | 5 | 9 | 2 |
       +---+---+---+---+---+---+---+
               |---------------|
                  Query [2,5]
```

The answer is:

```text
4 + 1 + 5 + 9 = 19
```

### Naive approach

The straightforward solution iterates through the requested interval.

```text
FUNCTION rangeSum(A, left, right):
    sum = 0

    FOR i FROM left TO right:
        sum = sum + A[i]

    RETURN sum
```

The time complexity depends on the interval size:

```text
T(n) = O(right - left + 1)
```

In the worst case, the query covers the entire array:

```text
O(n)
```

That may be acceptable for a single query.

But consider a system processing one million range-sum queries over a large array.

Repeatedly traversing the same elements performs substantial redundant computation.

**Can the array be preprocessed so that each query takes constant time?**

Yes.

## 2. The key idea: cumulative sums

Instead of storing only the original array, construct another array containing the sum of all elements seen so far.

Consider:

```text
A = [3, 1, 4, 1, 5, 9, 2]
```

Its cumulative sums are:

```text
A[0] = 3                     ->  3
A[0] + A[1]                  ->  4
A[0] + ... + A[2]            ->  8
A[0] + ... + A[3]            ->  9
A[0] + ... + A[4]            -> 14
A[0] + ... + A[5]            -> 23
A[0] + ... + A[6]            -> 25
```

The resulting prefix-sum array is:

```text
Index:   0   1   2   3   4   5   6

A:       3   1   4   1   5   9   2
         |   |   |   |   |   |   |
         v   v   v   v   v   v   v
Prefix:  3   4   8   9  14  23  25
```

Each entry in `Prefix` represents the sum of all elements from index `0` through that index.

Formally:

```text
P[i] = sum(A[j], j = 0..i)
```

For example:

```text
P[5] = 3 + 1 + 4 + 1 + 5 + 9 = 23
```

**The important observation is that these cumulative sums contain enough information to calculate arbitrary ranges without iterating through their elements.**

## 3. How a range sum becomes a subtraction

Return to the original query:

```text
Sum of A[2..5]
```

The required elements are:

```text
Index:   0   1   2   3   4   5   6
       +---+---+---+---+---+---+---+
A:     | 3 | 1 | 4 | 1 | 5 | 9 | 2 |
       +---+---+---+---+---+---+---+
               |---------------|
                     Wanted
```

First, calculate the sum of everything from index `0` through index `5`.

```text
         +-------------------+
         |                   |
         v                   v
A:       3   1   4   1   5   9   2
       |-----------------------|
                  P[5]

P[5] = 23
```

But that sum includes elements that precede the desired interval.

Specifically:

```text
A:       3   1   4   1   5   9   2
       |-------|
          P[1]

P[1] = 4
```

Subtracting the unwanted prefix leaves exactly the desired range.

```text
Entire prefix:
[3, 1, 4, 1, 5, 9] = 23

Unwanted prefix:
[3, 1]             =  4

Remaining range:
      [4, 1, 5, 9] = 19
```

Therefore:

```text
rangeSum(l, r) = P[r] - P[l - 1]
```

For the example:

```text
rangeSum(2, 5) = P[5] - P[1]
```

```text
= 23 - 4 = 19
```

This computation requires only two array lookups and one subtraction.

**The query is now `O(1)`, regardless of the interval size.**

## 4. A cleaner implementation: the leading-zero technique

The previous representation has a small inconvenience.

What happens when the query starts at index `0`?

The formula becomes:

```text
P[r] - P[-1]
```

But index `-1` is invalid in many array implementations.

A cleaner approach is to allocate a prefix-sum array with one additional element, initialized to zero.

```text
Original array:

Index:   0   1   2   3   4   5   6
A:       3   1   4   1   5   9   2

Prefix array:

Index:   0   1   2   3   4   5   6   7
P:       0   3   4   8   9  14  23  25
         ^
    Empty prefix
```

Now define:

```text
P[i] = sum(A[j], j = 0..i-1)
```

**Here, `P[i]` stores the sum of the first `i` elements, not the sum through index `i`.**

The range-sum formula becomes:

```text
rangeSum(l, r) = P[r + 1] - P[l]
```

**This convention eliminates the special case for ranges beginning at zero.**

### Pseudocode: building prefix sums

```text
FUNCTION buildPrefixSums(A):
    n = length(A)

    P = new array of size n + 1
    P[0] = 0

    FOR i FROM 0 TO n - 1:
        P[i + 1] = P[i] + A[i]

    RETURN P
```

### Pseudocode: answering range queries

```text
FUNCTION rangeSum(P, left, right):
    RETURN P[right + 1] - P[left]
```

**Assume `0 <= left <= right < length(A)`.**

For example:

```text
P = [0, 3, 4, 8, 9, 14, 23, 25]

rangeSum(P, 2, 5)
    = P[6] - P[2]
    = 23 - 4
    = 19
```

This half-open prefix convention is particularly convenient for reasoning about array boundaries.

## 5. Why prefix sums work: the invariant

The prefix-building loop maintains an important invariant:

> **After processing the first `i` elements, `P[i]` contains their sum.**

Mathematically:

```text
P[i] = sum(A[j], j = 0..i-1)
```

### Initialization

Before processing any elements:

```text
P[0] = 0
```

The sum of zero elements is zero.

Therefore, the invariant holds.

### Maintenance

Assume:

```text
P[i] = A[0] + A[1] + ... + A[i - 1]
```

The next operation is:

```text
P[i + 1] = P[i] + A[i]
```

Therefore:

```text
P[i + 1] = A[0] + A[1] + ... + A[i]
```

The invariant continues to hold.

### Termination

After processing all `n` elements:

```text
P[n] = sum(A[j], j = 0..n-1)
```

Every stored prefix is correct.

For any valid range `[l, r]`, the prefix `P[r+1]` consists of the elements before `l` plus the elements from `l` through `r`.

Subtracting `P[l]` removes exactly the preceding elements.

Hence:

```text
P[r + 1] - P[l] = sum(A[j], j = l..r)
```

This establishes the correctness of the range-query operation.

## 6. Time and space complexity

Prefix sums separate computation into two stages.

### Preprocessing

Building the prefix array requires one traversal of the original array.

```text
T_build(n) = O(n)
```

The additional prefix array stores `n + 1` values.

```text
S(n) = O(n)
```

### Querying

Every range query performs:

```text
P[right + 1] - P[left]
```

Therefore:

```text
T_query = O(1)
```

### Comparison

| Operation             | Naive approach    | Prefix sums       |
| --------------------- | ----------------- | ----------------- |
| Preprocessing         | `O(1)`            | `O(n)`            |
| Range sum             | `O(n)` worst case | `O(1)`            |
| Extra space           | `O(1)`            | `O(n)`            |
| Single-element update | `O(1)`            | `O(n)` worst case |

For `q` queries over an array of size `n`:

**Naive approach:**

```text
O(q * n)
```

**Prefix sums:**

```text
O(n + q)
```

Consider:

```text
n = 1,000,000 elements
q = 1,000,000 range queries
```

In a worst-case scenario:

```text
Naive:
    1,000,000 * 1,000,000
    = 1,000,000,000,000 element visits

Prefix sums:
    1,000,000 elements for preprocessing
    + O(1) operations per query
```

This is an enormous improvement when the array is read frequently and modified rarely.

## 7. The fundamental tradeoff: reads versus writes

Prefix sums work extremely well for immutable arrays.

But consider changing one element:

```text
Original:

A:       3   1   4   1   5   9   2
P:       0   3   4   8   9  14  23  25
```

Now update:

```text
A[2] = 10
```

The updated array is:

```text
A:       3   1  10   1   5   9   2
```

The new prefix sums are:

```text
P:       0   3   4  14  15  20  29  31
                   |-------------------|
                    All affected values
```

**Every prefix sum that includes `A[2]` must change.**

The number of affected entries can be proportional to `n`.

Consequently:

- Range queries are `O(1)`.
- Point updates can take `O(n)`.

This creates a classic data-structure tradeoff.

| Data structure | Range sum  | Point update |
| -------------- | ---------- | ------------ |
| Plain array    | `O(n)`     | `O(1)`       |
| Prefix sums    | `O(1)`     | `O(n)`       |
| Fenwick tree   | `O(log n)` | `O(log n)`   |
| Segment tree   | `O(log n)` | `O(log n)`   |

All complexities are worst-case for valid operations.

**Engineering principle:** Optimize for the workload rather than for an isolated operation.

An immutable dataset with millions of range queries strongly favors prefix sums. A dataset with frequent updates may justify a more sophisticated structure.

## 8. Prefix sums as a general problem-solving technique

The technique becomes more interesting when range sums are used to solve other problems.

### Example A: finding subarrays with a target sum

Consider:

```text
A = [2, 3, 1, 2, 4]
target = 6
```

The prefix sums are:

```text
Index:   0   1   2   3   4   5
P:       0   2   5   6   8  12
```

The sum of a subarray `[l, r)` is:

```text
P[r] - P[l]
```

We want:

```text
P[r] - P[l] = 6
```

Rearrange:

```text
P[l] = P[r] - 6
```

This transforms the problem.

Instead of examining every possible subarray, search for a previously encountered prefix sum equal to:

```text
currentPrefix - target
```

A hash map can track how many times each prefix sum has appeared.

```text
FUNCTION countSubarrays(A, target):
    counts = new hash map
    counts[0] = 1

    prefix = 0
    answer = 0

    FOR value IN A:
        prefix = prefix + value

        needed = prefix - target

        answer = answer + counts.getOrDefault(needed, 0)

        counts[prefix] = counts.getOrDefault(prefix, 0) + 1

    RETURN answer
```

Assuming expected `O(1)` hash-map operations:

- **Time:** `O(n)` expected.
- **Extra space:** `O(n)`.

**This works even when the array contains negative numbers.**

The crucial observation is that a subarray sum is the **difference between two prefix sums**.

### Example B: prefix sums over counts

Prefix sums do not need to represent sums of arbitrary numbers.

Suppose the task is to count how many even numbers appear in a range.

```text
A:       3   6   2   7   8   5

IsEven:  0   1   1   0   1   0

Prefix:  0   0   1   2   2   3   3
```

The count of even numbers in `[1, 4]` is:

```text
P[5] - P[1] = 3 - 0 = 3
```

The same technique works for counting occurrences, measuring frequencies, or aggregating binary conditions.

### Example C: two-dimensional prefix sums

Prefix sums extend naturally to matrices.

Consider:

```text
Matrix:

       c0  c1  c2
     +---+---+---+
r0   | 1 | 2 | 3 |
     +---+---+---+
r1   | 4 | 5 | 6 |
     +---+---+---+
r2   | 7 | 8 | 9 |
     +---+---+---+
```

Suppose the task is to calculate the sum of a rectangular region.

A two-dimensional prefix matrix stores the sum of all cells above and to the left of each position, using an extra zero row and column.

For a zero-based matrix:

```text
P[i + 1][j + 1] = A[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
```

The subtraction prevents double-counting the overlapping upper-left region.

Once constructed, the sum of any rectangle with inclusive corners `(r1, c1)` and `(r2, c2)` is:

```text
S = P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]
```

The preprocessing complexity is `O(rows * columns)`, and each rectangular range query takes `O(1)`.

This technique is useful for image processing, spatial aggregation, grids, and multidimensional analytical queries.

## 9. Important limitations and pitfalls

### Integer overflow

Prefix sums can become much larger than individual array elements.

For example:

```text
A = [1,000,000,000,
     1,000,000,000,
     1,000,000,000]
```

The total sum is three billion, which exceeds the maximum signed 32-bit integer.

**The prefix array must use a sufficiently wide numeric type.**

### Incorrect indexing

**The two conventions must not be mixed.**

```text
Convention 1:

P[i] = sum(A[0..i])

rangeSum(l, r) = P[r] - P[l - 1]
```

```text
Convention 2:

P[0] = 0
P[i + 1] = P[i] + A[i]

rangeSum(l, r) = P[r + 1] - P[l]
```

The second convention is generally easier to implement because it avoids special handling when `l = 0`.

### Prefix sums require an appropriate operation

**The technique is not limited to addition, but answering arbitrary ranges by removing a prefix requires a suitable inverse.**

For sums, the inverse is subtraction.

For XOR, the inverse is XOR itself.

For minimum values, there is no general inverse operation that removes an earlier prefix minimum. Thus, two prefix-minimum values cannot generally determine the minimum of an arbitrary interval.

## Core takeaway

Prefix sums illustrate a powerful algorithmic pattern:

```text
  Repeated expensive work
             |
             v
Identify shared computation
             |
             v
     Precompute results
             |
             v
    Reuse those results
             |
             v
   Faster future queries
```

The fundamental transformation is:

```text
Range aggregation = Prefix at end - Prefix before start
```

This is an example of trading `O(n)` preprocessing and additional memory for `O(1)` queries.

The deeper lesson is that **sometimes the fastest way to perform repeated computation is to avoid performing it repeatedly at all.**
