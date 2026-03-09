# Two pointers

Use two index variables to traverse an array simultaneously, reducing
$O(n^2)$ nested loops to a single $O(n)$ pass. The pointers advance
based on logical conditions rather than fixed iteration.

## Collision (opposite ends)

One pointer starts at index 0, the other at the last index. On a sorted
array the pointers form a narrowing funnel: moving left increases the
value, moving right decreases it. They converge until they meet.

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

## Fast and slow (tortoise and hare)

Both pointers start at the beginning. The fast pointer scans every
element; the slow pointer advances only when the fast pointer finds a
qualifying element. The slow pointer marks the boundary of the
processed region.

Use for:

- Removing duplicates from a sorted array in place
- Cycle detection in linked lists or sequences
- Finding the middle element in one pass

```java
int removeDuplicates(int[] nums) {
    int slow = 0;

    for (int fast = 1; fast < nums.length; fast++) {
        if (nums[fast] != nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }

    return slow + 1; // length of unique segment
}
```

## When to apply

| Problem signal          | Pattern          |
|-------------------------|------------------|
| Sorted array            | Collision        |
| In-place / $O(1)$ space | Fast and slow    |
| Pairs or triplets       | Sort + collision |
| Contiguous subarray     | Equi-directional |

## Related

- [Sliding window](sliding-window.md) - Equi-directional variant in depth
- [Arrays](arrays.md) - Underlying data structure

---

Return to [Data structures and algorithms](_index.md)
