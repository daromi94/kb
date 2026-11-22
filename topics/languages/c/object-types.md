# Object types

In C, an **object type** is a type that describes objects: regions of storage whose contents can represent values.

C distinguishes two principal categories:

- **Object types:** Describe objects.
- **Function types:** Describe functions.

**An object type may be _complete_ or _incomplete_, depending on whether enough information is available to determine the size of objects of that type.**

## 1. Understanding object types

Consider:

```c
int x = 42;
double y = 3.14;
int *p = &x;
```

Three objects exist, with different types.

```text
Identifier   Object contents   Type

             +-----------+
x ---------> | 42        |     int
             +-----------+

             +-----------+
y ---------> | 3.14      |     double
             +-----------+

             +-----------+
p ---------> | &x        |     int *
             +-----------+
                   |
                   v
                Object x
```

The type determines important properties of the object:

- **Size:** How much storage its representation requires.
- **Alignment:** Which addresses are valid for storing the object.
- **Representation:** How values are encoded in storage.
- **Operations:** Which operations are permitted on values of that type.
- **Interpretation:** How an expression of that type interprets stored data.

For example, `int` and `double` may both occupy four or more bytes, but their value representations and arithmetic semantics differ.

## 2. Classification of object types

The C type system organizes commonly used object types into the following categories.

```text
Object types
|
+-- Scalar types
|   |
|   +-- Arithmetic types
|   |   |
|   |   +-- Integer types
|   |   |   +-- char
|   |   |   +-- signed / unsigned integers
|   |   |   +-- bool
|   |   |   +-- enumerations
|   |   |
|   |   +-- Floating types
|   |       +-- Real floating
|   |       +-- Complex floating
|   |
|   +-- Pointer types
|   |
|   +-- nullptr_t (C23)
|
+-- Aggregate types
|   |
|   +-- Array types
|   +-- Structure types
|
+-- Union types
```

This tree describes the primary usable categories. C also defines qualified and atomic types, and special incomplete object types such as `void`.

## 3. Scalar types

A **scalar type** describes a single scalar value, rather than a collection of member objects.

Scalar types include arithmetic types, pointer types, and `nullptr_t` in C23.

### Arithmetic types

Arithmetic types support numerical operations.

```c
int count = 10;
double temperature = 36.5;
unsigned int flags = 7;
```

Integer types include `char`, signed and unsigned integer types, `_Bool`/`bool`, and enumerations.

Floating types include `float`, `double`, `long double`, and conditionally supported complex and decimal floating types.

C23 also introduces bit-precise integer types:

```c
_BitInt(12) number = 100;
```

Here, the integer type has a specified width of 12 bits. The object's total storage size may be greater.

### Pointer types

A pointer type describes an object whose value references another entity.

```c
int x = 10;
int *p = &x;
```

```text
Object p                     Object x
+------------+               +------------+
| Address    | ------------> |     10     |
+------------+               +------------+

Type: int *                  Type: int
```

An important distinction:

**A pointer object has its own type, storage, and lifetime.**

The pointed-to object is separate.

Additionally, pointers can refer to functions:

```c
int square(int x) {
    return x * x;
}

int (*operation)(int) = square;
```

`operation` is a pointer object.

`square` is a function, not an object.

## 4. Aggregate types

C defines two aggregate type categories:

- Array types
- Structure types

**An aggregate object contains member or element objects.**

### Array types

An array type represents a contiguous sequence of objects having the same element type.

```c
int numbers[3] = {10, 20, 30};
```

```text
Array object: numbers
Type: int[3]

+-----------+-----------+-----------+
|    10     |    20     |    30     |
+-----------+-----------+-----------+
     int         int         int
   object      object      object
```

**The array is one object containing three element objects.**

For an array of `N` elements of type `T`:

```text
sizeof(array) = N * sizeof(T)
```

This applies to complete, ordinary array types and to variable-length arrays once their bounds are established.

### Structure types

A structure type describes an object containing an ordered sequence of member objects.

```c
struct Point {
    int x;
    int y;
};

struct Point point = {10, 20};
```

```text
Structure object: point
Type: struct Point

+-------------------+
| x = 10            |
+-------------------+
| y = 20            |
+-------------------+
```

In actual memory, structures may contain padding between or after members to satisfy alignment requirements.

Each member can have a different type:

```c
struct Record {
    int id;
    double score;
    char status;
};
```

**A structure object is a single object containing member subobjects.**

## 5. Union types

**A union describes overlapping member storage.**

```c
union Value {
    int integer;
    float decimal;
};
```

Unlike a structure, whose members occupy separate regions, union members overlap in storage.

```text
Structure                  Union

+---------------+          +---------------+
| int integer   |          | int integer   |
+---------------+          |       OR      |
| float decimal |          | float decimal |
+---------------+          +---------------+

Separate storage           Overlapping storage
```

For example:

```c
union Value value;

value.integer = 42;
```

The union stores the representation associated with `integer`.

Accessing a different member requires care because its interpretation can involve representation-dependent behavior.

**C classifies unions separately from aggregates**, even though a union can have several members.

## 6. Complete versus incomplete object types

An object type can be complete or incomplete.

A **complete type** provides enough information to determine an object's size.

```c
int x;
struct Point p;
```

Assuming `struct Point` has already been fully defined, both are complete object types.

An **incomplete type** does not yet provide enough information to determine the size of its objects.

Consider:

```c
struct Node;

struct Node *head;
```

At this point:

- `struct Node` is an incomplete type.
- `struct Node *` is a complete pointer type.
- The object `head` can be defined because its pointer type is complete.

Later:

```c
struct Node {
    int value;
    struct Node *next;
};
```

The structure type becomes complete.

```text
Before definition:

struct Node
+-----------------------+
| Size unknown          |
| Members unknown       |
+-----------------------+

struct Node *head
+-----------------------+
| Pointer object        |
| Size known            |
+-----------------------+

After definition:

struct Node
+-----------------------+
| int value             |
| struct Node *next     |
+-----------------------+

Size and alignment known
```

A key consequence is that a pointer to an incomplete object type is valid, even though defining an ordinary object of that incomplete type is not yet possible.

### The special case of `void`

**C23 classifies `void` as an incomplete object type that cannot be completed.**

```c
void *p;
```

This is valid because `p` has pointer type.

But:

```c
void x;  // Invalid
```

An object cannot be defined with type `void`, because `void` does not provide a size or a set of representable values.

## 7. Qualified and atomic object types

C also supports qualified types.

Consider:

```c
int x = 10;
const int y = 20;
volatile int status = 0;
```

The qualifiers impose additional rules.

| Qualifier  | Meaning                                                       |
| ---------- | ------------------------------------------------------------- |
| `const`    | Prevents modification through that qualified lvalue           |
| `volatile` | Requires accesses to follow the language's volatile semantics |
| `restrict` | Expresses pointer-based aliasing requirements                 |
| `_Atomic`  | Provides atomic object access semantics                       |

For example:

```c
_Atomic int counter = 0;
```

An atomic type may have different size, alignment, and representation requirements from its corresponding non-atomic type.

**Qualifiers do not introduce different storage durations.**

A `const int` object can still have automatic, static, or other applicable storage duration.

## 8. Object types versus function types

Consider:

```c
int square(int x) {
    return x * x;
}

int number = 10;
```

`number` is an object.

`square` is a function.

```text
C entities
|
+-- Object
|   |
|   +-- number
|       Type: int
|       Has object storage
|
+-- Function
    |
    +-- square
        Type: function(int) returning int
        Has executable behavior
```

Function types describe callable functions, not objects holding ordinary stored values.

An expression designating a function can often be converted to a function pointer, but the function does not thereby become an object.

## 9. Object type versus storage duration

An object's type and storage duration answer different questions.

Consider:

```c
int global = 10;

void example(void) {
    int local = 20;
    static int persistent = 30;
}
```

All three objects have the same type: `int`.

However, they differ in storage duration.

| Object       | Type  | Storage duration |
| ------------ | ----- | ---------------- |
| `global`     | `int` | Static           |
| `local`      | `int` | Automatic        |
| `persistent` | `int` | Static           |

Type describes what kind of value the object represents and the associated rules.

Storage duration determines how long its storage exists.

These properties are independent.

## Fundamental mental model

```text
Object
|
+-- Type
|   |
|   +-- Scalar
|   +-- Aggregate
|   |   +-- Array
|   |   +-- Struct
|   +-- Union
|
+-- Storage duration
    |
    +-- Automatic
    +-- Static
    +-- Thread
    +-- Allocated

Type:
- Representation
- Size
- Alignment
- Allowed operations

Storage duration:
- When storage exists

Lifetime:
- When a particular object exists
```

The central principle is:

**An object is a region of storage. Its type determines how values associated with that storage are represented and interpreted, while its storage duration determines its lifetime.**
