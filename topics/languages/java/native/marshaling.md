# Marshaling

Marshaling is the process of converting data between JVM heap
representation and native memory layout when crossing the
Java/C boundary. Native functions cannot operate on Java objects
directly — they expect raw, contiguous, unmanaged memory.

## Data representation mismatch

| Aspect   | Java                         | C                            |
|----------|------------------------------|------------------------------|
| Strings  | `byte[]` (Latin-1 or UTF-16) | `char*` (UTF-8, null-termed) |
| Arrays   | Objects with length + bounds | Pointer to first element     |
| Lifetime | GC-managed, relocatable      | Fixed address, manual free   |

## Java to C (outbound)

Passing a String or array to a native function requires copying
data out of the heap:

1. Allocate an off-heap MemorySegment via an Arena
2. Copy and encode the data (e.g., Java string to UTF-8 bytes)
3. Append a null terminator for C strings
4. Pass the segment's address to the downcall

`allocateFrom(String)` handles steps 1-3 in a single call,
producing a null-terminated UTF-8 C string in off-heap memory.

This is always a copy. The C function operates on an independent
off-heap duplicate of the Java data.

## C to Java (inbound)

When a native function returns a pointer (e.g., `char*`):

1. The downcall returns a MemorySegment with size zero — raw
   pointers carry no length information
2. Call `reinterpret(newSize)` to assign usable spatial bounds,
   or use `getString(offset)` which scans for the null terminator
3. Copy and decode the bytes into a Java String or array

```java
// Reading a C string returned from a native function
String result = returnedSegment.getString(0);
```

## Performance

Marshaling is O(n) in data size — it allocates, encodes, and
copies. For small strings, overhead is negligible. For large
buffers (images, network payloads), repeated marshaling negates
the benefit of native execution.

The high-performance pattern is to keep large data permanently
off-heap, passing MemorySegment pointers between Java and C
instead of marshaling the underlying bytes.

---

Return to [Native interop](_index.md)
