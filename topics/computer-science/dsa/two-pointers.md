# Two pointers

Two index variables traverse an array simultaneously, turning
$O(n^2)$ nested scans into a single $O(n)$ pass. Each pointer
advances based on a condition, not a fixed step.

## Collision (opposite ends)

One pointer starts at 0, the other at the last index. On a sorted
array, moving left increases the value and moving right decreases it,
so the pointers converge toward the answer.

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

## Fast and slow

Both start at the beginning. Fast scans every element; slow advances
only when fast finds a qualifying element. Slow marks the boundary of
the processed region.

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
