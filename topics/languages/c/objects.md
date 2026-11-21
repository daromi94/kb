# Objects

An **object** is:

> A region of data storage in the execution environment, the contents of which can represent values.

In simpler terms, **an object is a region of storage that can hold a value.**

This definition is fundamental to C because the language's memory model is built around objects, their types, their representations, and their lifetimes.

## 1. Understanding the definition

Consider:

```c
int x = 42;
```

This declaration introduces three distinct concepts:

- **Object:** The region of storage associated with `x`.
- **Type:** `int`, which determines how the stored representation is interpreted.
- **Value:** `42`, the value stored in the object.

Assuming a machine where `int` occupies four 8-bit bytes, and using a hypothetical address:

```text
Object: x
Type:   int
Value:  42
Size:   4 bytes

Memory (illustrative little-endian representation):

Address       Contents
+------------+----------+
| 0x1000     | 00101010 | --+
| 0x1001     | 00000000 |   | Object x
| 0x1002     | 00000000 |   |
| 0x1003     | 00000000 | --+
+------------+----------+
```

The object is **not the number 42**. It is the storage that represents the number 42.

If the program executes:

```c
x = 100;
```

The same object now contains a representation of `100`.

**Its value changed, but its identity as an object did not.**

## 2. Object vs. variable

These concepts are closely related but are not interchangeable.

**A variable is a named object.** However, **not every object needs a name**.

For example:

```c
int x = 10;
```

Here `x` names an object.

Now consider:

```c
#include <stdlib.h>

int *p = malloc(sizeof(int));

if (p != NULL) {
    *p = 10;
    free(p);
}
```

There are two relevant objects:

1. **`p`:** A named object whose value is a pointer.
2. **The allocated object:** Storage obtained through `malloc`, without a declared name.

```text
    Named object
   +------------+
p  |  0x2000    |
   +------------+
          |
          | points to
          v
   +------------+
   |     10     |  Allocated object
   +------------+
       0x2000
```

**The allocated object has no declared type.** Accesses through typed expressions such as `*p` are governed by C's effective-type rules.

This distinction is particularly important for understanding pointers, dynamic allocation, and aliasing.

## 3. Objects can contain other objects

An object does not have to represent a single scalar value.

Consider an array:

```c
int numbers[3] = {10, 20, 30};
```

There are four objects of interest:

- The array object `numbers`.
- The element object `numbers[0]`.
- The element object `numbers[1]`.
- The element object `numbers[2]`.

```text
           Array object: numbers
+-------------+-------------+-------------+
| numbers[0]  | numbers[1]  | numbers[2]  |
|     10      |     20      |     30      |
+-------------+-------------+-------------+
  int object    int object    int object
```

The three element objects occupy regions within the larger array object.

The same principle applies to structures:

```c
struct Point {
    int x;
    int y;
};

struct Point p = {10, 20};
```

```text
        Structure object: p
+----------------+----------------+
|      p.x       |      p.y       |
|       10       |       20       |
+----------------+----------------+
```

This illustrates an important property of C's object model: **objects may contain subobjects**.

## 4. Objects have lifetimes

An object's storage is not necessarily available throughout the entire program.

C defines four storage durations:

| Storage duration | Typical example                               |
| ---------------- | --------------------------------------------- |
| Automatic        | Local variables                               |
| Static           | Global variables and local `static` variables |
| Thread           | Objects declared `thread_local`               |
| Allocated        | Objects created through `malloc`              |

Consider:

```c
void example(void) {
    int x = 10;
}
```

The object `x` has automatic storage duration.

Its lifetime ends when execution leaves the associated block.

By contrast:

```c
int *p = malloc(sizeof(int));
```

On successful allocation, the allocated object's lifetime lasts until that allocation is deallocated.

**Accessing an object outside its lifetime produces undefined behavior.**

## 5. An object is not necessarily a physical memory location

C's memory model uses an **abstract machine** rather than a specific CPU architecture.

For example:

```c
int add(int x) {
    int result = x + 1;
    return result;
}
```

**Semantically, `result` is an object.**

However, an optimizing compiler might:

- Keep the value in a CPU register.
- Eliminate the object from the generated machine code.
- Compute the result directly without reserving a stack slot.

**Therefore, the existence of an object in the C abstract machine does not imply that a distinct physical memory allocation must appear in the executable.**

## 6. Object vs. value vs. expression

Consider:

```c
int x = 10;
int y = x + 5;
```

Three distinctions matter:

| Concept           | Example                     | Explanation                                    |
| ----------------- | --------------------------- | ---------------------------------------------- |
| Object            | Storage associated with `x` | Holds a representation of a value              |
| Value             | `10`                        | Abstract information represented by the object |
| Expression        | `x + 5`                     | Computes a value                               |
| Lvalue expression | `x`                         | Designates an object                           |

The expression `x + 5` produces a value, but that result is not necessarily a distinct object.

This leads to a particularly important C concept: an **lvalue** is an expression that potentially designates an object.

For example:

```c
int x = 10;
int *p = &x;

*p = 20;
```

Both `x` and `*p` designate the same object.

```text
Expression x ----+
                 |
                 v
             +-------+
             |  20   |  Object
             +-------+
                 ^
                 |
Expression *p ---+
```

**The expressions are different, but the object is the same.**

## The fundamental mental model

```text
                  C Abstract Machine
                           |
                           v
                        Objects
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
     Type              Lifetime             Storage
       |                                       |
       v                                       v
Interpretation                          Representation
       |                                       |
       +-------------------+-------------------+
                           |
                           v
                         Value
```

**An object is the storage-bearing entity, a type governs how its contents are interpreted, and a value is what those contents represent.**
