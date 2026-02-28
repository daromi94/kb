# Thread memory

The fundamental tension in concurrent programming comes from the distinction
between what threads share (the process address space) and what each thread
owns privately (its execution context).

## Shared state (process scope)

A process is the primary unit of resource allocation. In Java, this corresponds
to the JVM instance. All threads within that JVM share:

**Heap:** All objects created with `new` reside here. Because the address space
is shared, a reference to an object can be passed from one thread to another.

**Method area:** Contains class-level data, the constant pool, and machine code
compiled by the JIT that threads execute.

**System resources:** File descriptors, socket handles, and signal handlers are
owned by the process. If one thread closes a FileInputStream, another thread will
encounter an IOException upon trying to read from it.

## Thread-private state (execution context)

Each thread maintains its own hardware context, enabling independent execution
and preemptive multitasking.

**Program counter:** A register holding the address of the current instruction.
For non-native methods, the PC tracks the bytecode instruction being executed.

**JVM stack:** Each thread is allocated a private stack upon creation. Every
method invocation pushes a new frame onto this stack. Each frame contains a
local variable array—since the stack is private, primitive local variables
(e.g., `int x = 5`) are physically unreachable by other threads.

**Native method stack:** Used for JNI calls to C/C++ code.

## The shared-vs-private boundary

While local variables are private, object references stored in those local
variables point to the shared heap. This is where the private boundary can be
breached.

```java
public void execute() {
    // 'list' is a local variable on the private stack.
    // The ArrayList object it points to is on the shared heap.
    List<String> list = new ArrayList<>();

    // If 'list' is passed to another thread, the "private"
    // boundary is breached via the shared heap.
}
```

**Stack confinement:** If a reference never escapes the thread that created it,
the object is effectively thread-safe without synchronization. This is the
foundation of confinement-based thread safety.

## Concurrency implications

**Race conditions:** Occur when multiple threads modify shared heap state
simultaneously without a happens-before relationship.

**Context switching:** The OS must save the PC and registers of the current
thread and load the context of the next. This involves kernel-mode transitions
and is computationally expensive.

**Memory visibility:** Threads have private registers and potentially private
CPU caches. Changes to shared heap memory may not be immediately visible to
other threads without explicit synchronization.

## Related

- [Thread safety hazards](thread-safety-hazards.md) - Race conditions, visibility, and reordering
- [Threads](threads.md) - Thread fundamentals and creation

---

Return to [Concurrency](_index.md)
