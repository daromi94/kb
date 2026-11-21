# Variables

A **variable** in C is commonly understood as a named object: a region of storage associated with an identifier and used to represent a value.

There is an important distinction:

- **Object** is a formally defined concept.
- **Variable** is commonly used terminology.

An identifier can denote an object. This is the foundation of what programmers ordinarily call a variable.

## 1. Understanding a variable

Consider:

```c
int x = 42;
```

This declaration introduces several concepts:

| Concept | Meaning                                   |
| ------- | ----------------------------------------- |
| `int`   | The object's declared type                |
| `x`     | The identifier that names the object      |
| `42`    | The initial value                         |
| Object  | The region of storage associated with `x` |

Assuming `sizeof(int) == 4`, an illustrative memory layout is:

```text
 C source code
  int x = 42;
       |
       v
+-------------+
| Identifier  |
|      x      |
+-------------+
       |
       | denotes
       v
+-------------+
|   Object    |
|             |
| Value: 42   |
| Type: int   |
| Size: 4 B   |
+-------------+
```

**The identifier `x` provides a way to refer to the object.**

**The object itself holds the representation of the value.**

These are distinct concepts.

## 2. A variable is not the value it contains

Consider:

```c
int x = 10;

x = 20;
x = 30;
```

Conceptually:

```text
Time T1:
    x
    |
    v
+------+
|  10  |
+------+

Time T2:
    x
    |
    v
+------+
|  20  |
+------+

Time T3:
    x
    |
    v
+------+
|  30  |
+------+
```

The identifier continues to designate the same object throughout these assignments.

The object's stored value changes.

This gives rise to an important distinction:

**Assignment normally changes the value stored in an existing object; it does not create a new object.**

## 3. Variables, identifiers, and objects are different

Consider:

```c
int x = 10;
int *p = &x;
```

Two named objects exist:

- `x`, an `int` object.
- `p`, a pointer object containing the address of `x`.

```text
Identifier p                Identifier x
      |                           |
      v                           v
+----------+                +----------+
| 0x1000   |--------------->|    10    |
+----------+                +----------+
   Pointer                     Integer
   object                      object
```

The pointer `p` is itself a variable. Its value is an address.

**The expression `*p` designates the object named `x`, but it does not introduce another variable or object.**

```c
*p = 50;
```

After this assignment, `x == 50`.

Two distinct expressions, `x` and `*p`, can designate the same object.

## 4. Not every object is a variable

Consider dynamic memory allocation:

```c
#include <stdlib.h>

int *p = malloc(sizeof(int));

if (p != NULL) {
    *p = 42;
    free(p);
}
```

On successful allocation, there are two objects:

```text
Named object
     p
+---------+
| Address |
+---------+
     |
     v
+---------+
|   42    |
+---------+
Allocated object (no identifier)
```

The pointer object is named `p`.

The allocated storage provides an object without a declared identifier.

Therefore:

**All ordinary variables denote objects, but not all objects have variable names.**

## 5. Variables do not necessarily change

The term _variable_ might suggest that its value must be modifiable.

That is not true in C.

```c
const int limit = 100;
```

`limit` names an object whose declared type is `const int`.

**It cannot legally be modified after initialization.**

```c
limit = 200;  // Constraint violation
```

A `const`-qualified object is still an object, and `limit` is still commonly called a variable.

**The ability to modify an object is separate from the existence of the object.**

## 6. Variables have scope and storage duration

Two independent properties govern how named objects behave.

**Scope** determines where an identifier can be used in source code.

**Storage duration** determines how long an object's storage exists.

Consider:

```c
int global = 10;

void example(void) {
    int local = 20;
    static int counter = 0;

    counter++;
}
```

| Variable  | Scope | Storage duration |
| --------- | ----- | ---------------- |
| `global`  | File  | Static           |
| `local`   | Block | Automatic        |
| `counter` | Block | Static           |

```text
Program execution
|
+-- global object exists -------------------+
|                                           |
|    example() called                       |
|    |                                      |
|    +-- local object exists -+             |
|    |                        |             |
|    +-- function returns ----+             |
|                                           |
|    example() called again                 |
|    |                                      |
|    +-- new local object ----+             |
|    |                        |             |
|    +-- function returns ----+             |
|                                           |
+-- program terminates ---------------------+

counter exists throughout execution,
despite having block scope.
```

**Consequently, an object's lifetime and the visibility of its identifier are not the same thing.**

## 7. Declaration versus definition

Consider:

```c
extern int count;
```

This declares the identifier `count` as referring to an `int` object defined elsewhere.

**It does not, by itself, define the object.**

By contrast:

```c
int count = 0;
```

This is a definition of `count`.

**A definition of an object causes storage to be reserved for it in the C abstract machine.**

## The fundamental distinction

```text
Declaration / Definition
            |
            v
       Identifier
            |
            | denotes
            v
         Object
            |
            | contains a
            | representation of
            v
          Value
```

The essential concepts are:

- **Identifier:** A name used in source code.
- **Object:** A region of data storage.
- **Value:** The information represented by an object's contents.
- **Variable:** The conventional term for a named object.

A particularly useful mental model for C is:

**A variable is a name associated with an object, not a name associated directly with a value.**
