# Pointers

A **pointer** is a value that can designate an object or a function. A pointer object is an object whose type is a pointer type and whose stored value can be used to access another object or function.

Pointers provide C with a fundamental capability: **indirection**.

Instead of accessing an object directly through its identifier, a program can access it indirectly through a pointer.

```c
int x = 42;
int *p = &x;
```

Here:

- `x` is an object of type `int`.
- `p` is an object of type `int *`.
- `&x` produces a pointer to `x`.
- `*p` is an expression that designates the object `x`.

## 1. Understanding pointers

Consider:

```c
int x = 42;
int *p = &x;
```

Assume `x` occupies memory at address `0x1000`, `p` occupies memory at `0x2000`, and the implementation represents pointers using addresses.

```text
Object p                    Object x
Type: int *                 Type: int

Address: 0x2000             Address: 0x1000
+--------------+            +--------------+
| 0x1000       | ---------> | 42           |
+--------------+            +--------------+
```

Notice that there are **two distinct objects**.

The pointer object `p` has its own storage, value, type, and lifetime.

The object `x` has its own storage, value, type, and lifetime.

The value stored in `p` allows the program to designate `x`.

This distinction is fundamental:

**A pointer is not the object it points to. It is a value through which that object can be accessed.**

Conventional architectures commonly represent pointers as numeric addresses. Other representations are possible.

## 2. The address-of and indirection operators

Two operators are essential for understanding pointers.

| Operator | Name        | Meaning                                                   |
| -------- | ----------- | --------------------------------------------------------- |
| `&`      | Address-of  | Produces a pointer to the designated object               |
| `*`      | Indirection | Dereferences a pointer to designate the referenced object |

Consider:

```c
int x = 10;

int *p = &x;

int y = *p;
```

The expressions have the following meanings:

```text
Expression   Meaning
----------   ------------------------
x            Designates object x
&x           Produces pointer to x
p            Evaluates to pointer to x
*p           Designates object x
y            Designates object y
```

After initialization:

```text
x = 10
y = 10

p ----> x
```

The expression `*p` does not necessarily read the value of `x`.

It is an **lvalue expression** that designates the object.

Whether a read or write occurs depends on how the expression is used.

For example:

```c
int y = *p;  // Read x through p

*p = 20;     // Write x through p
```

The initializer reads the stored value of `x`.

The assignment modifies the original object.

## 3. Pointer types

Pointers have types.

Consider:

```c
int x = 10;
double y = 3.14;

int *p = &x;
double *q = &y;
```

The declarations introduce two different pointer types:

```text
int *p
    |
    +-- Pointer to int

double *q
    |
    +-- Pointer to double
```

**The type of a pointer determines which type of object is expected when dereferencing it.**

For example:

```c
int *p = &x;

*p = 50;
```

The expression `*p` has type `int`.

The compiler uses this information to enforce type rules and generate the required operations.

Importantly, the pointer's type does not imply that all pointer types have the same size or representation.

On many 64-bit systems:

```text
sizeof(int *) == 8
```

Pointer size and representation can vary with the implementation and the pointed-to type.

## 4. Pointers and object identity

Consider:

```c
int x = 10;

int *p = &x;
int *q = &x;
```

There are three objects:

- `x`, an integer object.
- `p`, a pointer object.
- `q`, another pointer object.

However, both pointer values designate the same object.

```text
+------------+
| p = &x     | ------------+
+------------+             |
                           |            +------------+
                           +----------> | x = 10     |
                           |            +------------+
+------------+             |
| q = &x     | ------------+
+------------+
```

Now consider:

```c
*p = 20;

printf("%d\n", *q);
```

Output:

```text
20
```

Why?

**Because `*p` and `*q` designate the same object.**

This is called **aliasing**: two or more expressions provide access to the same storage.

Aliasing becomes important in compiler optimization, memory safety, concurrency, and the rules governing effective types.

## 5. Pointers themselves are passed by value

Consider:

```c
void increment(int *p) {
    *p += 1;
}

int main(void) {
    int x = 10;

    increment(&x);
}
```

The function receives a copy of a pointer value.

```text
main()                          increment()
+----------------+              +----------------+
| x = 10         | <----------- | p = &x         |
+----------------+              +----------------+
```

**The parameter `p` is a separate object.**

However, it designates the original object `x`.

Therefore:

```c
*p += 1;
```

modifies `x`.

This does not contradict C's pass-by-value semantics.

**C passes the pointer value, not the pointed-to object.**

### Changing the pointer itself

Consider:

```c
#include <stddef.h>

void change(int *p) {
    p = NULL;
}

int main(void) {
    int x = 10;
    int *ptr = &x;

    change(ptr);
}
```

After the function returns, `ptr` still points to `x`.

**The assignment `p = NULL` modifies only the parameter object `p`.**

To modify the caller's pointer object, another level of indirection is necessary.

## 6. Pointers to pointers

A pointer can designate another pointer object.

Consider:

```c
int x = 10;

int *p = &x;
int **pp = &p;
```

```text
Object pp            Object p             Object x
Type: int **         Type: int *          Type: int

+------------+       +------------+       +------------+
| &p         | ----> | &x         | ----> | 10         |
+------------+       +------------+       +------------+
```

**Each level of indirection removes one pointer level from the expression's type.**

| Expression | Type     | Meaning        |
| ---------- | -------- | -------------- |
| `pp`       | `int **` | Pointer to `p` |
| `*pp`      | `int *`  | Designates `p` |
| `**pp`     | `int`    | Designates `x` |

For example:

```c
**pp = 100;
```

This modifies the original object `x`.

After execution:

```text
x == 100
```

Pointer-to-pointer parameters are useful when a function needs to modify another pointer object.

```c
void reset(int **pp) {
    *pp = NULL;
}
```

**Calling `reset(&p)` changes `p` itself.**

**It does not free the object that `p` previously pointed to.**

## 7. Pointers and arrays

Pointers and arrays are closely related, but **an array is not a pointer**.

Consider:

```c
int values[3] = {10, 20, 30};
int *p = values;
```

In this initialization, the array expression `values` is converted to a pointer to its first element.

Conceptually:

```text
Array object: values
Illustrative addresses with 4-byte int objects

    0x1000        0x1004        0x1008
+-------------+-------------+-------------+
|  values[0]  |  values[1]  |  values[2]  |
|     10      |     20      |     30      |
+-------------+-------------+-------------+
       ^
       |
       |
+--------------+
| p = 0x1000   |
+--------------+
```

Now:

```text
*p        // values[0]
*(p + 1)  // values[1]
*(p + 2)  // values[2]
```

The expression:

```text
p + 1
```

does not mean adding one byte to the pointer's address representation.

**It means advancing by one element of the pointed-to type.**

If `sizeof(int) == 4`, this typically corresponds to moving four bytes forward.

### Pointer arithmetic is type-aware

```text
     p
     |
     v
+---------+---------+---------+
|   10    |   20    |   30    |
+---------+---------+---------+
  p + 0     p + 1     p + 2
```

Pointer arithmetic is defined within an array object, including the permitted one-past-the-end position.

```c
int *end = values + 3; // Valid one-past pointer
```

However:

```c
// int x = *end; // Undefined behavior
```

**Dereferencing a one-past-the-end pointer is invalid.**

Pointer arithmetic outside the permitted bounds is also undefined behavior, even if the resulting numeric address would happen to refer to mapped memory.

## 8. Null pointers

**A null pointer is a pointer value that does not designate an object or function.**

```c
int *p = NULL;
```

In C23:

```c
int *p = nullptr;
```

A null pointer can be used to represent the absence of a target.

```c
if (p != NULL) {
    printf("%d\n", *p);
}
```

**Dereferencing a null pointer produces undefined behavior.**

```c
int *p = NULL;

// *p = 10; // Undefined behavior
```

A null pointer is not necessarily represented by all-zero bits.

Null pointer semantics are independent of their physical representation.

## 9. Pointers and object lifetime

**A pointer does not extend the lifetime of the object it designates.**

Consider:

```c
int *p;

{
    int x = 42;
    p = &x;
}
```

When execution leaves the inner block, `x` reaches the end of its lifetime.

```text
Time       ------------------------------->

                         Block exits
                              |
                              v
Object x:  |==================|
Pointer p: |------------------------------>

Object x lifetime ends at block exit.
Object p remains alive.
```

The pointer object `p` remains alive, but the object it previously designated does not.

A pointer value becomes indeterminate when the object it points to, or one past it, reaches the end of its lifetime.

Therefore, a subsequent attempt to dereference `p` is undefined behavior.

Similarly:

```c
int *p = malloc(sizeof *p);

if (p != NULL) {
    *p = 42;

    free(p);
}
```

Calling `free(p)` on the allocation ends the lifetime of the allocated object.

It does not end the lifetime of the pointer object `p`.

This distinction explains dangling pointers and use-after-free errors.

## 10. Pointer qualifiers

The following declarations look similar but mean different things.

```c
const int *p;
int *const q = &some_int;
const int *const r = &some_int;
```

Assume `some_int` is a previously declared `int` object.

| Declaration          | Modify pointed-to integer through pointer? | Reassign pointer? |
| -------------------- | ------------------------------------------ | ----------------- |
| `const int *p`       | No                                         | Yes               |
| `int *const q`       | Yes                                        | No                |
| `const int *const r` | No                                         | No                |

**The distinction is between qualifying the pointed-to type and qualifying the pointer object itself.**

For example:

```c
int x = 10;
int y = 20;

const int *p = &x;

p = &y;   // Valid
// *p = 30; // Constraint violation
```

Here `p` can be reassigned, but modifying the integer through `p` is not permitted.

The `const` qualifier restricts access through a qualified lvalue; it does not necessarily mean that the underlying object is immutable through every possible alias.

## 11. Void pointers

**A `void *` is a generic object pointer type.**

```c
int x = 42;

void *p = &x;
```

A `void *` can hold a converted pointer to an object, but it cannot be directly dereferenced as an ordinary object pointer.

```c
// *p = 10;  // Invalid
```

To access the stored value, convert the pointer to a pointer to an appropriate complete object type.

```c
int *q = p;

*q = 100;
```

Now the original `x` object contains `100`.

This mechanism is particularly useful for generic allocation interfaces, such as `malloc`, and generic data structures.

It does not bypass C's effective-type and aliasing restrictions.

## 12. Pointers and physical memory

At the C language level, a pointer is a value used to designate an object or function.

At the machine level, pointers are commonly implemented as virtual addresses.

However, the language does not require:

- Every pointer to be a simple integer address.
- Every pointer type to have identical size.
- Every pointer representation to use the same format.
- Arbitrary integer values to be valid pointers.
- Every valid pointer value to be safe to dereference.

A pointer's validity depends on its value, its relationship to a live object or function, the access being performed, and the rules of the C abstract machine.

This distinction is essential when reasoning about undefined behavior and compiler optimizations.

## The fundamental mental model

```text
                   Pointer
                      |
        +-------------+-------------------+
        |                                 |
        v                                 v
  Pointer type                      Pointer value
        |                                 |
        v                                 v
Determines access                 Can designate an
 and arithmetic                  object or function
    semantics
                                          |
                                          v
                                     Indirection
                                          |
                                          v
                                  Access designated
                                 object or function
```

A pointer has two distinct roles:

**As an object:** A pointer variable occupies storage, has a type, contains a value, and has a lifetime.

**As a value:** A pointer can designate another object or function, enabling indirect access.

The most important principle is that **a pointer does not own, copy, or extend the lifetime of its target. It provides a way to refer to that target.**
