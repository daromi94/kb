# Two pointers

Two index variables traverse an array simultaneously, turning
$O(n^2)$ nested scans into a single $O(n)$ pass.

## Collision (opposite ends)

Start one pointer at index 0 and the other at the last index. Loop
while they haven't met. Each iteration, move one or both pointers
inward — which one depends on the problem.

The loop runs at most $O(n)$ iterations because the pointers start
$n$ apart and close by at least one step each iteration. If the work
per iteration is $O(1)$, the total is $O(n)$.

On a sorted array this is especially powerful: moving left increases
the value at left, moving right decreases the value at right. If the
current pair overshoots the target, moving right is the only way to
reduce it — left can only grow. This lets you eliminate candidates
without checking every pair.

```
left = 0
right = length - 1

while left < right:
    // compare or combine arr[left] and arr[right]
    // move left++, right--, or both
```

Use for:

- Pairs that sum to a target in a sorted array
- Reversing elements in place
- Partitioning (e.g., Dutch national flag)

```java
int[] twoSum(int[] nums, int target) {
    int left = 0, right = nums.length - 1;

    while (left < right) {
        int sum = nums[left] + nums[right];

        if (sum == target) {
            return new int[]{left, right};
        } else if (sum < target) {
            left++;
        } else {
            right--;
        }
    }

    return new int[]{-1, -1};
}
```

## Read/write (partitioning)

Both pointers start at the beginning. Fast advances every iteration,
scanning each element. Slow advances only when fast finds a qualifying
element. Everything before slow is the "processed" region — this
partitions the array in place without extra space.

The loop runs exactly $n$ iterations (fast visits every element once).
If the work per iteration is $O(1)$, the total is $O(n)$.

```
slow = 0

for fast in range(length):
    if qualifies(arr[fast]):
        arr[slow] = arr[fast]
        slow++

// arr[0..slow-1] contains the kept elements
```

Use for:

- Removing duplicates from a sorted array in place
- Filtering elements (e.g., move zeroes to end)
- In-place partitioning

```java
int removeDuplicates(int[] nums) {
    int slow = 0;

    for (int fast = 1; fast < nums.length; fast++) {
        if (nums[fast] != nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }

    return slow + 1; // Length of unique segment
}
```

## Tortoise and hare (speed-based)

Both pointers start at the beginning and advance every iteration, but
at different speeds — slow moves one step, fast moves two. Because
fast covers ground twice as quickly, the two pointers reveal structural
properties of the sequence.

```
slow = head
fast = head

while fast != null AND fast.next != null:
    slow = slow.next      // 1 step
    fast = fast.next.next // 2 steps
    if slow == fast:
        return true // cycle detected

return false // no cycle

// variant: skip the equality check and run to completion
// — when fast hits the end, slow is at the midpoint
```

Use for:

- Cycle detection (Floyd's algorithm) — if a cycle exists, the
  pointers will meet inside it
- Finding the middle element in one pass — when fast reaches the
  end, slow is at the midpoint
- Finding the cycle start — after detection, reset one pointer to
  head and advance both at speed 1 until they meet

## Two-input traversal

One pointer per input, both starting at index 0. Loop while both
pointers are in bounds. Each iteration, advance one or both pointers
— which one depends on the problem.

The main loop stops when either pointer reaches the end, so the other
input may have remaining elements. If all elements must be processed,
drain the unfinished input with a secondary loop.

```
i = j = 0

while i < a.length AND j < b.length:
    // compare a[i] and b[j]
    // advance i++, j++, or both

// drain remainder — only one of these runs
while i < a.length:
    // process a[i]; i++

while j < b.length:
    // process b[j]; j++
```

Runs in $O(n + m)$ time when the work per iteration is $O(1)$,
because each step advances at least one pointer and the pointers
cannot advance more than $n + m$ times total.

Use for:

- Merging two sorted arrays
- Subsequence checking
- Set intersection/union on sorted inputs

```java
int[] merge(int[] a, int[] b) {
    int[] result = new int[a.length + b.length];
    int i = 0, j = 0, k = 0;

    while (i < a.length && j < b.length) {
        if (a[i] <= b[j]) {
            result[k++] = a[i++];
        } else {
            result[k++] = b[j++];
        }
    }

    while (i < a.length) result[k++] = a[i++];
    while (j < b.length) result[k++] = b[j++];

    return result;
}
```

## When to apply

| Problem signal        | Pattern             |
|-----------------------|---------------------|
| Sorted array          | Collision           |
| Pairs or triplets     | Sort + collision    |
| In-place filter/dedup | Read/write          |
| Cycle detection       | Tortoise and hare   |
| Find middle element   | Tortoise and hare   |
| Contiguous subarray   | Equi-directional    |
| Two sorted inputs     | Two-input traversal |
| Subsequence check     | Two-input traversal |

## Limitations

Two pointers rely on structure in the data — sorted order,
partitioning, or a monotonic property — to skip work. If no such
structure exists and every pair must be examined, the technique does
not help.

## Related

- [Sliding window](sliding-window.md) - Equi-directional variant in depth
- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
