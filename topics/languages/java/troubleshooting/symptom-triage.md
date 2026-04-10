# Symptom triage

Java memory problems fall into distinct categories, and the diagnostic
path differs for each. Classify the symptom before reaching for tools.

## OutOfMemoryError types

The OOM message itself is the first clue:

| Message                              | Region    | Meaning                      |
|--------------------------------------|-----------|------------------------------|
| `Java heap space`                    | Heap      | Heap is full                 |
| `GC overhead limit exceeded`         | Heap      | GC is thrashing              |
| `Metaspace`                          | Metaspace | Class loading exhaustion     |
| `Direct buffer memory`               | Off-heap  | NIO/direct buffer exhaustion |
| `unable to create new native thread` | Native    | Native memory or ulimit hit  |

## Symptom categories

**OutOfMemoryError.** The JVM ran out of a specific memory region. The
error message tells you which one.

**High heap usage, stable.** The app works but holds more than expected.
This is a sizing or accounting question, not a leak.

**Gradual growth over time.** Classic leak. Heap-after-Full-GC climbing
monotonically over days is the unambiguous signature.

**High RSS, normal heap.** Off-heap problem. RSS is 8GB but heap is
only 2GB — the answer is in native memory tracking, not heap dumps.

**Excessive GC activity.** Memory pressure causing CPU burn. If the GC
runs continuously with near-100% CPU, the JVM is in a GC death spiral,
spending all its cycles trying to free memory. Look for frequent Full
GC events that reclaim little to nothing.

## OOM killer vs OutOfMemoryError

If the process vanishes without a Java stack trace, the Linux OOM
killer likely terminated it. Check system logs (`dmesg` or
`/var/log/messages`). An OOM kill usually points to native memory
exhaustion or under-provisioned container limits, not a heap leak.

## Choosing the right tool

The decision maps from symptom to memory region to tool:

| Symptom                     | First tool                            |
|-----------------------------|---------------------------------------|
| Heap OOM or retention leak  | Heap dump + MAT dominator tree        |
| GC thrashing without OOM    | GC logs, then allocation profiling    |
| RSS bloat with healthy heap | NMT summary, then narrow by category  |
| Unclear                     | JFR continuous recording (covers all) |

The single biggest mistake is jumping to heap dumps for every memory
problem. Half the time the heap is fine and the answer is in NMT, GC
logs, or native profiling.

## Related

- [Memory accounting](memory-accounting.md) - Building a memory budget
- [Heap dump analysis](heap-dump-analysis.md) - MAT workflow and patterns
- [Off-heap diagnostics](off-heap-diagnostics.md) - Non-heap investigation
- [Allocation profiling](allocation-profiling.md) - Rate vs retention

---

Return to [Troubleshooting](_index.md)
