# Loop invariants

**A loop invariant is a property that remains true every time a loop reaches a particular point in its execution.**

Loop invariants are one of the most important techniques in computer science for reasoning about algorithm correctness.

The central idea is simple:

> Instead of checking whether an algorithm works for every possible input, identify a property that is preserved by every iteration and use it to prove that the algorithm produces the correct result.

## 1. The intuition

Consider an algorithm that calculates the sum of an array.

```text
FUNCTION sum(A):
    total = 0

    FOR i = 0 TO length(A) - 1:
        total = total + A[i]

    RETURN total
```

For example:

```text
A = [3, 5, 2, 4]

Initial state:
    total = 0

Iteration 0:
    total = 3

Iteration 1:
    total = 8

Iteration 2:
    total = 10

Iteration 3:
    total = 14
```

How can correctness be established without executing every possible input?

The answer is to find something that is always true during execution.

**Loop invariant:**

**At the beginning of iteration `i`, `total` equals the sum of all elements preceding `i`.**

Mathematically:

```text
total = sum(A[j], j = 0 to i-1)
```

This property describes exactly what has already been accomplished by the algorithm.

```text
           i
           |
           v
A = [3, 5, 2, 4]
     +--+
     |
     +-- Already processed

total = 3 + 5 = 8
```

At the beginning of iteration `i = 2`, the invariant holds because `total = 8`, which is the sum of the first two elements.

Notice an important distinction:

- The value of `total` changes.
- The invariant remains true.

**An invariant does not necessarily mean that a variable stays constant. It means that a relationship between variables remains valid.**

## 2. The three steps of a loop invariant proof

Proving a loop invariant follows the same general structure as mathematical induction.

1. **Initialization**

Prove the invariant holds before the first iteration.

2. **Maintenance**

Assume the invariant holds before an iteration. Prove that executing that iteration preserves it.

3. **Termination**

When the loop finishes, use the invariant and the loop's exit condition to establish the desired result.

The logical structure is:

```text
      Initialization
             |
             v
     Invariant is true
             |
             v
   +------------------+<--------------------------+
   | Execute one      |                           |
   | iteration        |                           |
   +------------------+                           |
             |                                    |
             v                                    |
   Invariant still true                           |
             |                                    |
             +---------------------> Repeat-------+
             |
             v
      Loop terminates
             |
             v
Invariant + exit condition
             |
             v
      Correct result
```

Let's apply all three steps to the summation algorithm.

### Initialization

Before the first iteration:

```text
i = 0
total = 0
```

The invariant says:

```text
total = sum(A[j], j = 0 to -1) = 0
```

The sum of zero elements is zero.

Therefore, the invariant holds.

### Maintenance

Assume the invariant holds at the beginning of iteration `i`:

```text
total = sum(A[j], j = 0 to i-1)
```

The loop executes:

```text
total = total + A[i]
```

After this operation:

```text
total = sum(A[j], j = 0 to i)
```

When the next iteration begins, its index is `i + 1`.

The invariant for that iteration requires `total` to equal the sum of all elements before `i + 1`, which is precisely the sum just calculated.

Therefore, the invariant is preserved.

### Termination

The loop terminates when every element has been processed.

At that point:

```text
i = length(A)
```

The invariant tells us:

```text
total = sum(A[j], j = 0 to length(A)-1)
```

This is exactly the sum of the complete array.

The algorithm is correct.

Importantly, this proof works regardless of the array's values or length, assuming arithmetic does not overflow.

## 3. A more interesting example: finding the maximum

Consider the following algorithm:

```text
FUNCTION findMaximum(A):
    maximum = A[0]

    FOR i = 1 TO length(A) - 1:
        IF A[i] > maximum:
            maximum = A[i]

    RETURN maximum
```

Assume the array is nonempty.

The loop invariant is:

**At the beginning of iteration `i`, `maximum` is the largest element among `A[0]` through `A[i-1]`.**

Formally:

```text
maximum = max(A[0], ..., A[i-1])
```

Consider:

```text
A = [4, 9, 2, 7, 5]

i = 1:
[4] | 9  2  7  5
 ^
maximum = 4

i = 2:
[4  9] | 2  7  5
    ^
maximum = 9

i = 3:
[4  9  2] | 7  5
    ^
maximum = 9

i = 4:
[4  9  2  7] | 5
    ^
maximum = 9

Finished:
[4  9  2  7  5]
    ^
maximum = 9
```

The array is progressively divided into two regions:

```text
+----------------------+--------------------+
| Processed region     | Unprocessed region |
+----------------------+--------------------+
| Maximum is known     | Maximum unknown    |
+----------------------+--------------------+
```

Every iteration expands the processed region while preserving the guarantee that `maximum` represents its largest value.

This is a useful way to discover invariants:

**Identify what is already known about the processed portion of the input.**

## 4. Loop invariants in sorting algorithms

One of the classic applications is insertion sort.

```text
FUNCTION insertionSort(A):
    FOR i = 1 TO length(A) - 1:
        key = A[i]
        j = i - 1

        WHILE j >= 0 AND A[j] > key:
            A[j + 1] = A[j]
            j = j - 1

        A[j + 1] = key
```

The outer loop invariant is:

**At the beginning of iteration `i`, the prefix `A[0 ... i-1]` is sorted and contains exactly the elements originally in that prefix, possibly rearranged.**

Example:

```text
Original:
[7, 3, 5, 2]

i = 1:
[7] | 3  5  2
+-+
|
+-- sorted

After iteration:
[3, 7] | 5  2
+----+
|
+-- sorted

After next iteration:
[3, 5, 7] | 2
+-------+
|
+-- sorted

After final iteration:
[2, 3, 5, 7]
+----------+
|
+-- sorted
```

At every iteration, insertion sort takes one element from the unsorted region and inserts it into the correct position within the sorted region.

The loop invariant establishes that the sorted prefix grows without losing its sortedness.

At termination, the sorted prefix covers the entire array.

One subtlety matters: saying only "the prefix is sorted" is insufficient for a complete sorting proof. An algorithm might produce a sorted array while accidentally duplicating or losing elements. **The invariant must also establish that the elements are preserved.**

## 5. Loop invariants versus loop termination

There is an important distinction between proving that an algorithm produces the correct answer if it finishes and proving that it actually finishes.

Consider:

```text
WHILE true:
    total = total + 0
```

The invariant `total = 0` holds forever if `total` starts at zero.

But the algorithm never terminates.

**An invariant establishes preservation of a property; it does not guarantee progress.**

To prove termination, a common technique is to identify a loop variant: a nonnegative integer quantity that strictly decreases every iteration.

For example:

```text
FUNCTION countdown(n):
    WHILE n > 0:
        n = n - 1
```

A suitable loop variant is `n`, assuming the initial `n` is a nonnegative integer.

It cannot decrease indefinitely while remaining nonnegative, so the loop eventually terminates.

Together:

- **Loop invariant:** proves that the algorithm maintains correctness.
- **Loop variant:** helps prove that the algorithm eventually terminates.

**When an algorithm both terminates and returns the correct result, it has total correctness.**

## 6. How to discover loop invariants

Rather than guessing randomly, use a systematic approach.

For an algorithm that processes an array, ask:

1. What has already been processed at the beginning of an iteration?
2. What is guaranteed to be true about that processed region?
3. How does the next iteration preserve that guarantee?
4. When the loop ends, does the guarantee imply the desired result?

Common invariant patterns include:

| Algorithm      | Typical invariant                                                  |
| -------------- | ------------------------------------------------------------------ |
| Array sum      | Accumulator equals the sum of processed elements                   |
| Maximum search | Maximum equals the largest processed element                       |
| Linear search  | The target is absent from all previously examined elements         |
| Insertion sort | Processed prefix is sorted and preserves its elements              |
| Binary search  | If the target exists, it remains within the active search interval |
| Euclidean GCD  | The GCD of the current pair equals the GCD of the original pair    |

**The particularly powerful pattern is that each iteration reduces uncertainty while maintaining an established guarantee.**
