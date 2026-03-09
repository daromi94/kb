# Sliding window

Maintain a contiguous subarray "window" between a left and right
boundary that advances through the array. Only account for the element
entering the front and the element leaving the back — never recompute
the entire window. This turns an $O(n^2)$ brute-force scan into an
$O(n)$ single pass.

## Fixed-size window

The problem dictates the window length k. Build the initial window over
the first k elements, then slide one step at a time, adding the
incoming element and subtracting the outgoing one.

Use for:

- Maximum/average sum of a subarray of size k
- Finding anagrams in a string

```java
int maxSumOfSizeK(int[] arr, int k) {
    int maxSum = 0, windowSum = 0;

    for (int i = 0; i < k; i++) {
        windowSum += arr[i];
    }

    maxSum = windowSum;

    for (int i = k; i < arr.length; i++) {
        windowSum += arr[i] - arr[i - k];
        maxSum = Math.max(maxSum, windowSum);
    }

    return maxSum;
}
```

## Dynamic window

The window expands and shrinks based on a constraint. The right pointer
grows the window in a for loop; a while loop shrinks from the left
when the constraint is violated. Both boundaries advance at most n
times total, keeping the cost $O(n)$.

Use for:

- Longest substring with at most k distinct characters
- Smallest subarray with sum >= target

```java
int minSubArrayLen(int[] nums, int target) {
    int minLen = Integer.MAX_VALUE, windowSum = 0, left = 0;

    for (int right = 0; right < nums.length; right++) {
        windowSum += nums[right];

        while (windowSum >= target) {
            minLen = Math.min(minLen, right - left + 1);
            windowSum -= nums[left++];
        }
    }

    return minLen == Integer.MAX_VALUE ? 0 : minLen;
}
```

## When to update the answer

| Goal           | Update where           | Why                        |
|----------------|------------------------|----------------------------|
| Longest valid  | After the shrink loop  | Window is guaranteed valid |
| Shortest valid | Inside the shrink loop | Constraint still holds     |

## Pitfalls

**Frequency tracking.** For character-frequency problems, use
`new int[128]` instead of a HashMap. The array lookup is $O(1)$ with a
much smaller constant factor.

## Related

- [Arrays](arrays.md) - Underlying data structure
- [Two pointers](two-pointers.md) - General dual-index traversal
- [Prefix sums](prefix-sums.md) - Alternative for range queries

---

Return to [Data structures and algorithms](_index.md)
