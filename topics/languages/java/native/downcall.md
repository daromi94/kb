# Downcall

A downcall transitions execution from the JVM into a compiled
native function (typically C). The FFM API defines the entire
process in pure Java — no generated headers or separate native
source files required.

## Five-step process

### 1. Native linker

`Linker.nativeLinker()` returns a linker that conforms to the host
platform's ABI (calling convention). It handles register
assignment, stack layout, and return value placement for the
target architecture (x86_64, ARM64, etc.).

### 2. Symbol lookup

Native functions live in dynamic libraries (`.so`, `.dylib`,
`.dll`). A SymbolLookup locates them by name:

- `linker.defaultLookup()` — searches commonly used platform
  libraries (libc, libm, libdl on Linux)
- `SymbolLookup.loaderLookup()` — symbols loaded via
  `System.loadLibrary()`
- `SymbolLookup.libraryLookup("libcustom.so", arena)` — loads a
  specific library

`find(name)` returns an `Optional<MemorySegment>` pointing to the
function's entry address.

### 3. Function descriptor

FunctionDescriptor maps the C function's signature to Java layouts.
The first argument is the return layout; the rest are parameters:

```java
// size_t strlen(const char *s)
FunctionDescriptor desc = FunctionDescriptor.of(
    ValueLayout.JAVA_LONG, // return: size_t
    ValueLayout.ADDRESS    // param: const char*
);
```

Use `FunctionDescriptor.ofVoid(...)` for void-returning functions.

For pointer parameters that point to known data, attach a target
layout with `ADDRESS.withTargetLayout(layout)`. This lets the
returned MemorySegment carry correct spatial bounds:

```java
var byteArray = MemoryLayout.sequenceLayout(Long.MAX_VALUE, JAVA_BYTE);

FunctionDescriptor desc = FunctionDescriptor.of(
    ValueLayout.ADDRESS.withTargetLayout(byteArray),
    ValueLayout.ADDRESS.withTargetLayout(byteArray)
);
```

Function descriptors are platform-specific — native type sizes
vary across architectures. Use `Linker.canonicalLayouts()` to
discover the correct layout for each native primitive.

### 4. MethodHandle generation

The linker combines the function address and descriptor to produce
a MethodHandle — a low-level, JIT-optimizable callable reference
with performance comparable to JNI.

### 5. Invocation

Call `invokeExact()` on the handle. Marshal any pointer arguments
into off-heap memory via an Arena beforehand.

## Complete example

```java
import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;

Linker linker = Linker.nativeLinker();

MemorySegment strlenAddr = linker.defaultLookup().find("strlen").orElseThrow();

FunctionDescriptor desc = FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS);

MethodHandle strlen = linker.downcallHandle(strlenAddr, desc);

try (Arena arena = Arena.ofConfined()) {
    MemorySegment cStr = arena.allocateFrom("Project Panama");
    long len = (long) strlen.invokeExact(cStr); // 14
} catch (Throwable e) {
    throw new RuntimeException(e);
}
```

`invokeExact()` declares `throws Throwable`, requiring a catch
block or throws clause.

---

Return to [Native interop](_index.md)
