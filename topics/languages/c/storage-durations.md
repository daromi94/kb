# Storage durations

In C, **storage duration** is a property of an object that determines the period of program execution during which storage is reserved for that object.

C defines four storage durations:

1. **Automatic storage duration**
2. **Static storage duration**
3. **Thread storage duration**
4. **Allocated storage duration**

**Storage duration is closely related to an object's lifetime, but it is distinct from its type, scope, and linkage.**

## 1. Automatic storage duration

An object with automatic storage duration normally exists from entry into its associated block until execution leaves that block.

Consider:

```c
void example(void) {
    int x = 10;
    int y = 20;

    x += y;
}
```

Both `x` and `y` have automatic storage duration.

```text
          +---------------------------+
          | Execution                 |
          +-------------+-------------+
                        |
                        v
          +-------------+-------------+
          | Enter example()           |
          +---------------------------+
          |                           |
          | Object x exists           |
          | Object y exists           |
          |                           |
          | x = x + y                 |
          |                           |
          +-------------+-------------+
                        |
                        v
          +-------------+-------------+
          | Return from example()     |
          +-------------+-------------+
                        |
          +-------------+-------------+
          |                           |
          v                           v
+---------+---------+       +---------+---------+
| x lifetime ends   |       | y lifetime ends   |
+-------------------+       +-------------------+
```

**Each new invocation gets its own instances of these objects.**

For example, recursion creates distinct automatic objects for each active invocation:

```c
void recursive(int n) {
    int x = n;

    if (n > 0)
        recursive(n - 1);
}
```

```text
+-----------------------------------+
| recursive(2)                      |
+-----------------------------------+
| x = 2                             |
|                                   |
|   +---------------------------+   |
|   | recursive(1)              |   |
|   +---------------------------+   |
|   | x = 1                     |   |
|   |                           |   |
|   |   +-------------------+   |   |
|   |   | recursive(0)      |   |   |
|   |   +-------------------+   |   |
|   |   | x = 0             |   |   |
|   |   +-------------------+   |   |
|   +---------------------------+   |
+-----------------------------------+
```

**There are three distinct objects named `x`, one per active invocation.**

**Important:** **Automatic storage duration does not imply that an object must physically reside on the stack.** The compiler may use registers or optimize away storage, provided the program's observable behavior is preserved.

### Exception: variable-length arrays

```c
void example(int n) {
    int x = 10;

    int values[n];
}
```

**Unlike ordinary automatic objects, storage for the variable-length array `values` is allocated when execution reaches its declaration.**

Its lifetime ends when execution leaves its scope.

## 2. Static storage duration

An object with static storage duration exists throughout the entire execution of the program.

Consider:

```c
int global_count = 0;

void increment(void) {
    static int local_count = 0;

    global_count++;
    local_count++;
}
```

Both objects have static storage duration.

```text
+---------------------------------------+
| Program starts                        |
+-------------------+-------------------+
                    |
                    v
+-------------------+-------------------+
| global_count exists                   |
| local_count exists                    |
|                                       |
| increment()                           |
|   global_count = 1                    |
|   local_count  = 1                    |
|                                       |
| increment()                           |
|   global_count = 2                    |
|   local_count  = 2                    |
+-------------------+-------------------+
                    |
                    v
+-------------------+-------------------+
| Program terminates                    |
+---------------------------------------+
```

**The important distinction is that the `static` keyword is not required for every object with static storage duration.**

For example:

```c
int global = 10;
```

**At file scope, `global` has static storage duration even without the `static` keyword.**

Inside a function:

```c
void example(void) {
    static int x = 10;
}
```

`x` has block scope but static storage duration.

The name is visible only within its block, but the object exists throughout program execution.

**Static storage duration means persistent storage, not global visibility.**

**Objects with static storage duration are initialized once, before program startup.** If no explicit initializer is provided, they receive the default initialization specified by C (for example, zero for arithmetic types).

## 3. Thread storage duration

Thread storage duration was introduced in C11.

An object with thread storage duration exists throughout the execution of its associated thread.

**Each thread has its own distinct instance.**

In C23:

```c
thread_local int counter = 0;
```

In C11/C17, the corresponding spelling is `_Thread_local` (also available via the `thread_local` macro in `<threads.h>`).

Consider two threads executing:

```c
thread_local int counter = 0;

void increment(void) {
    counter++;
}
```

Conceptually:

```text
              +-------------------+
              | Program           |
              +---------+---------+
                        |
          +-------------+-------------+
          |                           |
          v                           v
+---------+---------+       +---------+---------+
| Thread A          |       | Thread B          |
+-------------------+       +-------------------+
| counter = 0       |       | counter = 0       |
|                   |       |                   |
| increment()       |       | increment()       |
| counter = 1       |       | counter = 1       |
|                   |       |                   |
| increment()       |       | increment()       |
| counter = 2       |       | counter = 2       |
+---------+---------+       +---------+---------+
          |                           |
          v                           v
+---------+---------+       +---------+---------+
| Thread A exits    |       | Thread B exits    |
+-------------------+       +-------------------+
```

Each thread owns a separate `counter` object.

**This differs from a global static-duration object, which is shared across threads.**

Thread-local storage is useful for maintaining per-thread state without passing that state through every function call.

**It does not, by itself, make operations on shared objects thread-safe.**

## 4. Allocated storage duration

Objects with allocated storage duration have storage obtained and released through memory-allocation functions.

Consider:

```c
#include <stdlib.h>

void example(void) {
    int *p = malloc(sizeof *p);

    if (p == NULL)
        return;

    *p = 42;

    free(p);
}
```

On successful allocation, two objects are involved:

- `p` has automatic storage duration.
- The object obtained through `malloc` has allocated storage duration.

```text
+---------------------------+
| Enter example()           |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Pointer object p          |
| Automatic duration        |
+-------------+-------------+
              |
              v
+-------------+-------------+
| malloc()                  |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Allocated storage         |
|                           |
| Value = 42                |
+-------------+-------------+
              |
              v
+-------------+-------------+
| free(p)                   |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Allocated lifetime ends   |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Return from example()     |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Pointer p lifetime ends   |
+---------------------------+
```

Allocated storage is particularly interesting because **its lifetime is independent of the block that requested the allocation**.

For example:

```c
#include <stdlib.h>

int *create_number(void) {
    int *p = malloc(sizeof *p);

    if (p != NULL)
        *p = 42;

    return p;
}

int main(void) {
    int *number = create_number();

    if (number != NULL) {
        free(number);
    }
}
```

**The object created by `malloc` can outlive the function invocation that allocated it.**

The local pointer `p` ceases to exist when `create_number` returns, but the allocated object remains alive until deallocated.

This is the fundamental reason dynamic allocation enables objects to outlive their creating functions.

**Calling `realloc` also ends the lifetime of the original allocated object on success, even if the resulting allocation uses the same address.**

## 5. Comparing all four storage durations

| Duration  | Begins                                         | Ends                                    |
| --------- | ---------------------------------------------- | --------------------------------------- |
| Automatic | Entry into associated block (ordinary objects) | Exit from block                         |
| Static    | Program execution begins                       | Program execution ends                  |
| Thread    | Associated thread starts                       | Associated thread ends                  |
| Allocated | Successful allocation                          | Deallocation or successful reallocation |

Their lifetimes can be visualized together:

```text
Time              ---------------------------------------------->

Program:          |=============================================|
Static:           |=============================================|
Thread A:              |=============================|
Thread B:                   |=============================|
Automatic object:              |=======|
Allocated object:        |==========================|
                         malloc                     free
```

The different storage durations determine the boundaries within which each object can exist.

## 6. Storage duration is not scope

Consider:

```c
int a = 10;

void example(void) {
    int b = 20;
    static int c = 30;
}
```

The properties are:

| Object | Scope | Storage duration |
| ------ | ----- | ---------------- |
| `a`    | File  | Static           |
| `b`    | Block | Automatic        |
| `c`    | Block | Static           |

**Scope describes where the identifier is visible.**

**Storage duration describes the period during which the object exists.**

Similarly, storage duration is distinct from **linkage**, which determines whether declarations of an identifier in different scopes or translation units can refer to the same entity.

## 7. Storage duration is not a physical memory region

The four storage durations are concepts of the C abstract machine.

They are not direct synonyms for particular hardware or operating-system memory regions.

A typical implementation might use:

```text
+-------------------------------------+
| Process virtual address space       |
+-------------------------------------+
|                                     |
| Stack                               |
|   Automatic objects                 |
|                                     |
+-------------------------------------+
|                                     |
| Free / mapped address space         |
|                                     |
+-------------------------------------+
|                                     |
| Heap                                |
|   Dynamically allocated objects     |
|                                     |
+-------------------------------------+
|                                     |
| Static data (.data / .bss)          |
|   Static-duration objects           |
|                                     |
+-------------------------------------+
|                                     |
| Thread-local storage (TLS)          |
|   Thread-duration objects           |
|                                     |
+-------------------------------------+
```

This is only an illustrative organization. C does not mandate a stack, heap, `.bss`, or TLS memory segment.

A compiler or runtime chooses how to implement these semantics.

## The fundamental mental model

```text
                         +-------------------+
                         | Object            |
                         +---------+---------+
                                   |
                                   v
                         +---------+---------+
                         | Storage duration  |
                         +---------+---------+
                                   |
        +-----------------+--------+--------+-----------------+
        |                 |                 |                 |
        v                 v                 v                 v
+-------+-------+ +-------+-------+ +-------+-------+ +-------+-------+
| Automatic     | | Static        | | Thread        | | Allocated     |
+---------------+ +---------------+ +---------------+ +---------------+
```

**Storage duration specifies the rules governing how long an object's storage exists.**

Three closely related ideas must remain separate:

- **Scope:** Where an identifier can be used.
- **Storage duration:** The category determining the availability of storage.
- **Lifetime:** The actual portion of execution during which a particular object exists.
