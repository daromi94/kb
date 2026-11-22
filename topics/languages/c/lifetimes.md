# Lifetimes

In C, an object's **lifetime** is the portion of program execution during which storage is guaranteed to be reserved for that object.

An object has three fundamental properties during its lifetime:

- The object **exists**.
- The object has a **constant address**.
- The object **retains its last-stored value**, except when that value is indeterminate.

**Lifetime is a runtime property** of an **object**, not of an identifier or a value.

## 1. Understanding object lifetime

Consider:

```c
void example(void) {
    int x = 10;

    x = 20;
    x = 30;
}
```

The object associated with `x` has automatic storage duration.

Its lifetime begins when execution enters the associated block and ends when execution leaves that block.

```text
+-------------------------------+
| Program execution             |
+---------------+---------------+
                |
                v
+---------------+---------------+
| Enter block                   |
|                               |
| Object x begins lifetime      |
|                               |
| int x = 10;                   |
|                               |
| x = 20;                       |
|                               |
| x = 30;                       |
|                               |
| Object x ends lifetime        |
+---------------+---------------+
                |
                v
+---------------+---------------+
| Continue execution            |
+-------------------------------+
```

Notice that assignment does not change the lifetime of the object.

```text
Time ------------------------------------------------->

+-------------------+         +-------------------+
| Lifetime begins   |         | Lifetime ends     |
+---------+---------+         +---------+---------+
          |                             |
          v                             v
          +-----------------------------+
Object x: | 10 ------> 20 ------> 30    |
          +-----------------------------+
```

The object exists throughout this interval, even though its value changes.

**An object's lifetime concerns its existence, not how many times its value changes.**

## 2. Lifetime versus scope

Lifetime and scope are fundamentally different concepts.

- **Scope** determines where an identifier is visible in source code.
- **Lifetime** determines when an object exists during execution.

Consider:

```c
void example(void) {
    {
        int x = 10;
    }
}
```

The identifier `x` has block scope.

The object denoted by `x` has automatic storage duration.

**For an ordinary automatic object that is not a variable-length array, its lifetime begins when execution enters the associated block, even if its declaration appears later.**

```c
void example(void) {
    // x is not in scope here.

    int x = 10;

    // x is now in scope.
}
```

Conceptually:

```text
+-----------------------------------+
| Block execution                   |
+-----------------------------------+
| Object lifetime starts            |
|                                   |
| +-------------------------------+ |
| | Storage for x exists          | |
| |                               | |
| | int x = 10;                   | |
| |     ^                         | |
| |     Identifier scope begins   | |
| |                               | |
| | x = 20;                       | |
| |                               | |
| +-------------------------------+ |
|                                   |
| Lifetime ends at block exit       |
+-----------------------------------+
```

The distinction is subtle: **an object can already be within its lifetime even though its identifier is not yet in scope.**

**Variable-length arrays are an exception: their automatic lifetime begins when their declaration is reached.**

## 3. Storage duration determines lifetime

C defines four storage durations, which determine how object lifetimes behave.

| Storage duration | Lifetime                                                      |
| ---------------- | ------------------------------------------------------------- |
| Automatic        | Generally, from entry to exit of the associated block         |
| Static           | Entire program execution                                      |
| Thread           | Entire execution of the associated thread                     |
| Allocated        | From successful allocation until deallocation or reallocation |

### Automatic lifetime

```c
void example(void) {
    int x = 10;
}
```

**Each invocation of `example()` creates a separate instance of `x`.**

```text
+---------------------+
| Call 1              |
+---------------------+
| x object exists     |
|                     |
| x = 10              |
+----------+----------+
           |
           v
+----------+----------+
| Lifetime ends       |
+---------------------+


+---------------------+
| Call 2              |
+---------------------+
| New x object        |
|                     |
| x = 10              |
+----------+----------+
           |
           v
+----------+----------+
| Lifetime ends       |
+---------------------+
```

The second invocation does not revive the object from the first invocation.

It creates a different object.

**The implementation may reuse the same memory address, but that does not make the two object instances identical.**

### Static lifetime

```c
void counter(void) {
    static int count = 0;

    count++;
}
```

The object `count` has static storage duration.

Its lifetime extends throughout program execution.

```text
+-----------------------------------------+
| Program starts                          |
+--------------------+--------------------+
                     |
                     v
+--------------------+--------------------+
| Object count exists                     |
|                                         |
| counter() -> count = 1                  |
| counter() -> count = 2                  |
| counter() -> count = 3                  |
|                                         |
| Program terminates                      |
+-----------------------------------------+
```

**Leaving the function does not end the object's lifetime.**

The next call accesses the same object.

### Allocated lifetime

```c
#include <stdlib.h>

void example(void) {
    int *p = malloc(sizeof *p);

    if (p == NULL) {
        return;
    }

    *p = 42;

    free(p);
}
```

**The allocated object's lifetime begins when `malloc` successfully returns and ends when the allocation is deallocated.**

```text
+---------------------+
| malloc()            |
+----------+----------+
           |
           v
+----------+----------+
| Allocated object    |
|                     |
| *p = 42             |
+----------+----------+
           |
           v
+----------+----------+
| free(p)             |
+----------+----------+
           |
           v
+----------+----------+
| Lifetime ends       |
+---------------------+
```

On successful allocation, there are two objects here:

- **`p`:** A pointer object with automatic storage duration.
- **The allocated object:** Designated by `*p` while its lifetime is active.

**These objects have different lifetimes.**

## 4. What happens when an object's lifetime ends?

When an object's lifetime ends, accessing that object results in **undefined behavior**.

Consider:

```c
int *get_number(void) {
    int x = 42;

    return &x;
}

int main(void) {
    int *p = get_number();

    int value = *p;  // Undefined behavior
}
```

During `get_number()`:

```text
+-------------------------+
| get_number()            |
+-------------------------+
|                         |
| x: [42]                 |
| ^                       |
| |                       |
| return &x               |
|                         |
+------------+------------+
             |
             v
+------------+------------+
| Function returns        |
+------------+------------+
             |
             v
+------------+------------+
| Lifetime of x ends      |
+------------+------------+
             |
             v
+------------+------------+
| main()                  |
+-------------------------+
|                         |
| p refers to an object   |
| whose lifetime ended    |
|                         |
| *p  --> UNDEFINED       |
|         BEHAVIOR        |
|                         |
+-------------------------+
```

**The fact that the physical bytes might still contain `42` does not matter.**

C's object model no longer recognizes a live `x` object there.

**Furthermore, a pointer value becomes indeterminate when the object it points to, or one past it, reaches the end of its lifetime.**

The problem is therefore more fundamental than merely reading old bytes.

## 5. Lifetime is not initialization

**An object can exist without having a determinate value.**

Consider:

```c
void example(void) {
    int x;

    x = 42;
}
```

The object `x` is within its lifetime before the assignment, but its initial value is indeterminate.

```text
Time ----------------------------------------------------------->

+-------------------+ +-------------------+ +-------------------+
| Block entry       | | Assignment        | | Block exit        |
+---------+---------+ +---------+---------+ +---------+---------+
          |                     |                     |
          v                     v                     v
          +---------------------+---------------------+
          | Object x exists     |                     |
          |                     |                     |
          | Indeterminate       | 42                  |
          |                     |                     |
          +---------------------+---------------------+
```

**Existence does not imply initialization.**

**An object's lifetime, its current value, and whether that value can safely be read are separate properties.**

## 6. Why lifetime matters for memory safety

Lifetime violations are a major source of errors in C.

Two common examples are:

**Use after free**

```c
int *p = malloc(sizeof *p);

if (p != NULL) {
    *p = 100;

    free(p);

    // *p = 200;  // Undefined behavior
}
```

**Returning a pointer to an automatic object**

```c
int *bad(void) {
    int value = 100;

    return &value;
}
```

**Both illustrate the same fundamental rule: a program must not access an object after its lifetime has ended.**

In contrast, returning a value is valid:

```c
int good(void) {
    int value = 100;

    return value;
}
```

**The return expression produces the integer value `100`.** The caller does not need the local object to remain alive.

## The fundamental mental model

```text
                        +-----------------+
                        | Object          |
                        +--------+--------+
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
         v                       v                       v
+--------+--------+     +--------+--------+     +--------+--------+
| Type            |     | Lifetime        |     | Value           |
+-----------------+     +-----------------+     +-----------------+
| How data        |     | When storage    |     | What data       |
| is treated      |     | exists          |     | represents      |
+-----------------+     +-----------------+     +-----------------+


                        +-----------------+
                        | Identifier      |
                        +--------+--------+
                                 |
                                 v
                        +--------+--------+
                        | Scope           |
                        +--------+--------+
                                 |
                                 v
                        +--------+--------+
                        | Where the name  |
                        | is accessible   |
                        +-----------------+
```

The essential principle is:

**Lifetime determines whether an object exists at a particular point during program execution. Scope determines whether an identifier can designate it at a particular point in source code.**

An object may be alive without its name being visible, and a pointer may remain in scope after the object it previously pointed to has ceased to exist.
