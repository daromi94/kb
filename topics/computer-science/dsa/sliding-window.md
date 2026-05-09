# Sliding window

A left and right boundary define a contiguous subarray that moves
through the input. Each step extends or shrinks the boundaries rather
than recomputing from scratch. This turns $O(n^2)$ brute-force into
$O(n)$.

## Fixed-size window

The window length k is given. Build the initial window over the first
k elements, then slide one position at a time:

Use for:

- Maximum/average sum of a subarray of size k
- Finding anagrams in a string

```java
int maxSumOfSizeK(int[] arr, int k) {
    int maxSum = 0, windowSum = 0;

    // Build initial window
    for (int i = 0; i < k; i++) {
        windowSum += arr[i];
    }

    maxSum = windowSum;

    // Slide: add incoming, drop outgoing
    for (int i = k; i < arr.length; i++) {
        windowSum += arr[i] - arr[i - k];
        maxSum = Math.max(maxSum, windowSum);
    }

    return maxSum;
}
```

## Dynamic window

The window expands and shrinks to satisfy a constraint. Right grows
the window in a for loop; a while loop shrinks from the left when the
constraint breaks. Each boundary advances at most n times total, so
the cost is $O(n)$.

Use for:

- Longest substring with at most k distinct characters
- Smallest subarray whose sum meets a target

```java
int minSubArrayLen(int[] nums, int target) {
    int minLen = Integer.MAX_VALUE, windowSum = 0, left = 0;

    for (int right = 0; right < nums.length; right++) {
        // Expand window
        windowSum += nums[right];

        // Shrink window while valid
        while (windowSum >= target) {
            minLen = Math.min(minLen, right - left + 1);
            windowSum -= nums[left++];
        }
    }

    return minLen == Integer.MAX_VALUE ? 0 : minLen;
}
```

## Limitations

The window must be a contiguous subarray — sliding window does not
apply to subsequences with gaps. The window property must also be
monotonic: expanding the window can only make the condition harder (or
easier) to satisfy, never both. If adding an element can both help
and hurt, the shrink logic breaks.

---

Return to [Data structures and algorithms](_index.md)
