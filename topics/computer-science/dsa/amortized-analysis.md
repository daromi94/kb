# Amortized analysis

Amortized analysis is a technique for analyzing the cost of a sequence of operations on a data structure, rather than analyzing each operation independently.

The central idea is:

> An operation can occasionally be expensive while the average cost per operation, over any sufficiently long sequence, remains small.

This is particularly useful when a data structure performs cheap operations most of the time but occasionally needs expensive maintenance, such as resizing, rebuilding, or reorganizing internal state.

## 1. The problem: occasional expensive operations

Consider a dynamic array, which grows automatically when it runs out of capacity.

An insertion normally requires writing one element:

```text
Array:
+----+----+----+----+
| 10 | 20 |    |    |
+----+----+----+----+
  0    1    2    3

size     = 2
capacity = 4
```

Appending `30` is cheap:

```text
+----+----+----+----+
| 10 | 20 | 30 |    |
+----+----+----+----+

Cost = 1 write
```

But suppose the array is full:

```text
+----+----+----+----+
| 10 | 20 | 30 | 40 |
+----+----+----+----+

size     = 4
capacity = 4
```

Appending another element requires allocating a larger array and copying existing elements.

```text
Old array:
          +----+----+----+----+
          | 10 | 20 | 30 | 40 |
          +----+----+----+----+
                    |
                    | Allocate new array
                    | Copy 4 elements
                    v
New array:
+----+----+----+----+----+----+----+----+
| 10 | 20 | 30 | 40 | 50 |    |    |    |
+----+----+----+----+----+----+----+----+

Cost = 4 copies + 1 write = 5
```

If the capacity is `n`, an insertion that triggers resizing costs `O(n)`.

Yet dynamic arrays typically provide amortized `O(1)` append.

How can an operation that sometimes takes `O(n)` time have an amortized cost of `O(1)`?

The answer comes from analyzing the entire sequence.

## 2. Worst-case versus amortized complexity

There are two different questions:

**Worst-case analysis:** How expensive can a single operation become?

**Amortized analysis:** How expensive are operations, on average, across a sequence, assuming the worst possible valid sequence of operations?

For a dynamic array that doubles its capacity:

| Measurement | Append complexity |
| ----------- | ----------------- |
| Best case   | `O(1)`            |
| Worst case  | `O(n)`            |
| Amortized   | `O(1)`            |

The important distinction is that amortized analysis is not probabilistic.

There are no assumptions about random inputs, probability distributions, or operations happening with certain frequencies.

**Amortized analysis provides a deterministic bound over sequences of operations.**

For example, an amortized `O(1)` bound means that `m` append operations have total cost `O(m)`, under the usual dynamic-array model.

**It does not mean every append costs `O(1)`.**

## 3. The aggregate method

The aggregate method is the simplest way to perform amortized analysis.

It follows three steps:

1. Consider a sequence of `m` operations.
2. Determine the total cost of the sequence.
3. Divide the total cost by `m`.

Mathematically:

```text
Amortized cost = (Total cost of operations) / m
```

### Example: dynamic array doubling

Suppose an array starts with capacity 1 and doubles whenever full.

```text
Operation     Capacity     Actual cost

append(1)         1             1
append(2)         2             2
append(3)         4             3
append(4)         4             1
append(5)         8             5
append(6)         8             1
append(7)         8             1
append(8)         8             1
append(9)        16             9
```

The expensive operations appear when capacity is exhausted.

```text
Copying costs on resize:

1 + 2 + 4 + 8 + 16 + ...

These costs grow geometrically.
```

For `m` appends, the total number of copied elements is bounded by:

```text
1 + 2 + 4 + ... + 2^k < 2*m
```

There are also exactly `m` writes of newly appended elements.

Therefore:

```text
T(m) < m + 2*m = 3*m
```

Consequently:

```text
T(m) = O(m)
```

Dividing by the number of operations:

```text
T(m) / m = O(1)
```

Conclusion: Even though an individual insertion can cost `O(n)`, the total cost of `m` insertions is `O(m)`.

### Why doubling matters

The resizing operations are expensive, but they become increasingly infrequent.

```text
Capacity:

1 --> 2 --> 4 --> 8 --> 16 --> 32
      ^     ^     ^      ^      ^
      |     |     |      |      |
      +-----+-----+------+------+
                  |
          resize operations

Number of ordinary appends between resizes grows.
```

**Each expensive resize creates enough spare capacity to support many cheap future appends.**

This is the fundamental mechanism behind amortization.

## 4. Three methods of amortized analysis

There are three classical approaches:

| Method     | Core idea                                          |
| ---------- | -------------------------------------------------- |
| Aggregate  | Bound the total cost of all operations             |
| Accounting | Charge extra for cheap operations and save credits |
| Potential  | Measure stored work using a mathematical function  |

All three can prove the same amortized bounds, but they provide different ways of understanding where the costs come from.

## 5. The accounting method

The accounting method imagines that operations pay into a credit balance.

Some cheap operations are intentionally overcharged. The excess credits are saved to pay for future expensive operations.

Consider the same doubling dynamic array.

Suppose each append is charged 3 units:

- 1 unit pays for inserting the new element.
- 2 units are saved to pay for future copying.

The idea is:

```text
         Charge: 3 units
                |
                v
         +-------------+
         |   Append    |
         +-------------+
                |
    +-----------+-----------+
    |                       |
    v                       v
 1 unit                  2 units
insertion             saved credits
```

When the array is full, accumulated credits pay for copying its contents into a larger array.

### Why 3 units are sufficient

Immediately after doubling capacity from `k` to `2*k`, the new array contains `k` elements.

Before the next resize, at least `k` new elements must be appended.

Those `k` operations save:

```text
2*k credits
```

The next resize requires copying `2*k` elements.

Therefore, the saved credits cover the copying cost.

For the initial small-capacity cases, the same charging scheme can maintain a nonnegative credit balance.

The amortized charge is always 3, a constant.

```text
Amortized append cost = O(1)
```

The accounting interpretation is useful because it separates two concepts:

**Actual cost:** How much work an operation really performs.

**Amortized charge:** How much cost is assigned to that operation after accounting for credits saved or spent.

**The amortized charge does not have to equal the actual cost.**

## 6. The potential method

The potential method formalizes the accounting idea.

Instead of imagining credits, it defines a mathematical function describing how much prepaid work is stored in the data structure.

This function is called the potential function:

```text
Phi(D)
```

Here, `D` represents the current state of the data structure.

The amortized cost of operation `i` is:

```text
c_hat_i = c_i + Phi(D_i) - Phi(D_(i-1))
```

Where:

- `c_i`: actual cost of the operation.
- `Phi(D_i)`: potential after the operation.
- `Phi(D_(i-1))`: potential before the operation.
- `c_hat_i`: amortized cost.

The intuition is:

```text
Potential increases:
    Cheap operation stores work for later.

Potential decreases:
    Expensive operation spends stored work.
```

### Dynamic array example

For an array that doubles when full, define:

```text
Phi(D) = 2*size - capacity
```

This is a useful potential for append-only arrays starting with size 0 and capacity 1. It starts at -1 and never falls below that initial value.

**Case A: Append without resizing**

The actual cost is 1.

Size increases by 1, while capacity remains unchanged.

Therefore:

```text
delta_Phi = 2
```

And:

```text
c_hat_i = 1 + 2 = 3
```

**Case B: Append with resizing**

Suppose the old array has size and capacity `k`.

The actual cost is:

```text
c_i = k + 1
```

The old potential is:

```text
Phi_before = 2*k - k = k
```

After resizing and appending, capacity becomes `2*k` and size becomes `k+1`.

The new potential is:

```text
Phi_after = 2*(k+1) - 2*k = 2
```

Therefore:

```text
delta_Phi = 2 - k
```

And:

```text
c_hat_i = (k+1) + (2-k) = 3
```

Despite the large copying cost, the amortized cost is constant.

### Why the potential method works

Summing amortized costs over `m` operations gives:

```text
sum(c_hat_i, i = 1 to m) = sum(c_i, i = 1 to m) + sum(Phi(D_i) - Phi(D_(i-1)), i = 1 to m)
```

The potential differences telescope:

```text
sum(c_hat_i, i = 1 to m) = sum(c_i, i = 1 to m) + Phi(D_m) - Phi(D_0)
```

Rearranging:

```text
sum(c_i, i = 1 to m) = sum(c_hat_i, i = 1 to m) + Phi(D_0) - Phi(D_m)
```

When the potential starts at zero and never becomes negative:

```text
sum(c_i, i = 1 to m) <= sum(c_hat_i, i = 1 to m)
```

**Thus, the sum of amortized costs is an upper bound on actual total work.**

This is a rigorous explanation of why cheap operations can pay for expensive future operations.

## 7. Another example: a binary counter

Consider a binary counter that increments by 1.

```text
0000
0001
0010
0011
0100
0101
0110
0111
1000
```

An increment can flip many bits.

For example:

```text
Before: 0111
After:  1000

Bits flipped = 4
```

For a counter of `n` bits, a single increment may require `O(n)` work.

However, over a long sequence:

- The least significant bit flips every increment.
- The next bit flips every second increment.
- The next bit flips every fourth increment.
- The next bit flips every eighth increment.

For `m` increments, total flips are bounded by:

```text
m + m/2 + m/4 + m/8 + ... < 2*m
```

Therefore:

```text
T(m) = O(m)
```

And:

```text
Amortized increment cost = O(1)
```

The important pattern is the same as dynamic array resizing:

**The expensive work occurs infrequently enough that its total cost is linear in the number of operations.**

## 8. When amortization does not work

Not every expensive operation can be amortized to constant time.

Suppose an array grows capacity by exactly one element every time it becomes full.

```text
Capacity:

1 --> 2 --> 3 --> 4 --> 5 --> 6
```

Appending the `k`-th element may require copying `k-1` existing elements.

After `m` insertions, the copying work is:

```text
1 + 2 + 3 + ... + (m-1)
```

Using the arithmetic-series formula:

```text
m*(m-1) / 2 = Theta(m^2)
```

Therefore:

```text
T(m) = Theta(m^2)
```

And:

```text
Amortized append cost = Theta(m)
```

The distinction:

| Growth strategy        | Total cost of `m` appends | Amortized append |
| ---------------------- | ------------------------- | ---------------- |
| Increase capacity by 1 | `Theta(m^2)`              | `Theta(m)`       |
| Double capacity        | `Theta(m)`                | `Theta(1)`       |

This explains why geometric growth strategies are common in dynamic data structures.

More generally, growing capacity by any fixed multiplicative factor greater than 1 produces amortized constant-time append, although the memory overhead and resizing frequency differ.

## 9. Why amortized analysis matters in systems engineering

Amortized analysis appears in numerous practical systems.

| System or data structure | Occasional expensive work | Amortization mechanism                                            |
| ------------------------ | ------------------------- | ----------------------------------------------------------------- |
| Dynamic arrays           | Reallocation and copying  | Geometric capacity growth                                         |
| Hash tables              | Resizing and rehashing    | Resizes separated by many insertions                              |
| Union-Find               | Path compression          | Structural changes reduce future work                             |
| Splay trees              | Tree rotations            | Potential-based structural analysis                               |
| Log-structured storage   | Compaction                | Data movement distributed across writes under a compaction policy |

However, an important limitation exists.

### Amortized efficiency does not guarantee low latency

A data structure can have excellent amortized complexity and still produce occasional high-latency operations.

Consider a service processing requests:

```text
Request 1       1 ms
Request 2       1 ms
Request 3       1 ms
Request 4       1 ms
Request 5     100 ms   <-- resizing or rebuilding
Request 6       1 ms
Request 7       1 ms
```

The average may remain low, but a particular request experiences a latency spike.

**Amortized bounds describe total work, not latency guarantees for individual operations.**

This distinction matters for:

- Tail-latency-sensitive services.
- Real-time systems.
- In-memory databases.
- Memory allocation.
- Garbage collection.
- Storage compaction.

Sometimes a system deliberately spreads maintenance across smaller incremental steps to avoid large pauses, even if the asymptotic amortized complexity remains unchanged.

**An amortized `O(1)` operation is not necessarily a worst-case `O(1)` operation.**

## 10. How to recognize an amortized analysis problem

Amortized analysis is a useful candidate when operations exhibit this pattern:

```text
           Many cheap operations
                     |
                     v
      Occasional expensive operation
                     |
                     v
 Expensive operation changes future state
                     |
                     v
Many cheap operations become possible again
```

The critical question is:

> Can the expensive work be charged to a sufficiently large number of cheap operations, or to distinct structural changes, so that each operation pays only a bounded amount?

A common mistake is assuming that rare expensive operations automatically imply constant amortized complexity.

They do not.

**The total cost must be proven.**

For example, repeatedly rebuilding an entire structure after every operation would not have constant amortized cost, even if the rebuild itself enables future work.

## Key takeaway

Amortized analysis establishes how the cost of expensive operations is distributed across a sequence of operations.

Three principles are worth retaining:

1. **Analyze sequences, not isolated operations.** An `O(n)` individual operation can belong to an `O(1)`-amortized data structure.
2. **Prove the total cost.** Cheap operations must occur frequently enough, or structural progress must be sufficient, to offset expensive work.
3. **Distinguish throughput from latency.** Amortized complexity can explain good overall efficiency without guaranteeing low worst-case execution time.

**The deeper insight is that the current state of a data structure contains information about how much expensive work can happen in the future. Amortized analysis turns that information into a mathematical bound.**
