# Pointer best practices

Pointers provide access to objects through indirection. Their flexibility comes with a fundamental responsibility: **C does not automatically enforce object lifetimes, ownership, bounds, or valid memory access.**

Reliable pointer-based code depends on maintaining several invariants:

- **A pointer must have a valid value before it is used.**
- **Its target must still be alive when accessed.**
- **Every access must respect the object's bounds, type, and alignment.**
- **Dynamically allocated storage must have clear ownership.**
- **Pointer arithmetic must remain within the bounds permitted by C.**

## 1. Always initialize pointers

An uninitialized automatic pointer object has an indeterminate value.

**Bad:**

```c
int *p;

*p = 42;  // Undefined behavior
```

**Good:**

```c
int *p = NULL;

int x = 42;
p = &x;
```

Initializing a pointer to `NULL` makes its initial state explicit.

However, **a non-null pointer is not necessarily valid**. It might refer to an object whose lifetime has ended or to storage that cannot be accessed through that pointer.

## 2. Never dereference a pointer without establishing its validity

Consider:

```c
void increment(int *p) {
    if (p != NULL) {
        ++*p;
    }
}
```

This handles the case where a null pointer is a permitted argument.

Dereferencing `p` also requires the following checks.

```text
+---------------------------+
| Pointer p                 |
+---------------------------+
              |
              v
+---------------------------+
| Is p non-null?            |
+---------------------------+
              |
              v
+---------------------------+
| Is its target alive?      |
+---------------------------+
              |
              v
+---------------------------+
| Is access in bounds?      |
+---------------------------+
              |
              v
+---------------------------+
| Is the access type-valid  |
| and properly aligned?     |
+---------------------------+
              |
              v
+---------------------------+
| Dereference               |
+---------------------------+
```

**A null check cannot detect dangling pointers, invalid addresses, or out-of-bounds pointers.**

A well-designed API should establish these guarantees through its contract.

## 3. Make pointer ownership explicit

**C pointers do not inherently express ownership.**

Consider:

```c
int *p = malloc(sizeof *p);
```

Who is responsible for calling `free`?

The language does not answer this question. The program's design must.

Three common ownership models are:

| Model                 | Meaning                                            |
| --------------------- | -------------------------------------------------- |
| Owning pointer        | Responsible for releasing the allocation           |
| Borrowed pointer      | May access the object but does not release it      |
| Transferred ownership | Responsibility moves from one component to another |

These are programming conventions, not special C pointer types.

For example:

```c
#include <stdlib.h>

void inspect(const int *p) {
    if (p != NULL) {
        // Read the integer
    }
}

int main(void) {
    int *p = malloc(sizeof *p);

    if (p == NULL) {
        return 1;
    }

    *p = 42;

    inspect(p);

    free(p);
}
```

Here, `main` owns the allocation.

`inspect` borrows access to the integer.

```text
main()              inspect()
   |                    |
   | owns allocation    | borrows access
   |                    |
   +--------+-----------+
            |
            v
+-----------------------+
| int object            |
| value = 42            |
+-----------------------+

main() calls free()
```

**Best practice:** Every dynamic allocation should have a clearly established deallocation responsibility.

## 4. Never return pointers to automatic local objects

**Bad:**

```c
int *create_value(void) {
    int x = 42;

    return &x;
}
```

The lifetime of `x` ends when the function returns.

**A pointer cannot extend that lifetime.**

```text
+-----------------------+
| create_value()        |
| x = 42                |
| return &x             |
+-----------------------+
            |
            v
+-----------------------+
| Lifetime ends         |
+-----------------------+
            |
            v
+-----------------------+
| Pointer no longer     |
| designates a live x   |
+-----------------------+
```

**Better: return the value directly.**

```c
int create_value(void) {
    return 42;
}
```

Or, when an independently allocated object is actually required:

```c
int *create_value(void) {
    int *p = malloc(sizeof *p);

    if (p != NULL) {
        *p = 42;
    }

    return p;
}
```

If allocation succeeds, the caller owns the returned allocation and must eventually release it.

Prefer returning ordinary values when dynamic allocation is unnecessary.

## 5. Use `const` to express read-only access

Consider:

```c
void print_value(const int *p);
```

This declaration expresses that the function does not modify the pointed-to integer through `p`.

Compare:

```c
void read_value(const int *p);
void modify_value(int *p);
```

The signatures communicate different permissions.

```text
const int *p
     |
     +-- Can read *p
     +-- Cannot modify *p through p

int *p
     |
     +-- Can read *p
     +-- Can modify *p
```

This is especially useful for structures:

```c
struct Config {
    int timeout;
    int retries;
};

void validate(const struct Config *config);
void reset(struct Config *config);
```

`validate` promises read-only access through its parameter.

`reset` may modify the structure.

Note that `const` does not guarantee that other aliases cannot modify the object.

## 6. Always associate array pointers with bounds

**A pointer to an array element does not carry the array's length.**

Consider:

```c
void process(int *values) {
    // How many elements are available?
}
```

The function cannot determine the array length from `values`.

A better interface is:

```c
#include <stddef.h>

void process(size_t count, int values[count]) {
    for (size_t i = 0; i < count; ++i) {
        values[i] *= 2;
    }
}
```

Here, the array parameter is adjusted to a pointer parameter, and `count` establishes the intended extent. The caller must still provide valid arguments.

Usage:

```c
int numbers[] = {1, 2, 3, 4};

process(sizeof numbers / sizeof numbers[0], numbers);
```

An alternative is:

```c
void process(int *values, size_t count);
```

The length is part of the interface contract.

```text
Array of four integers

values
   |
   v
+------+------+------+------+
|  1   |  2   |  3   |  4   |
+------+------+------+------+

count = 4
Valid element indices: 0, 1, 2, 3
```

This prevents reliance on assumptions about the size of a caller's array.

## 7. Use `sizeof *p` when allocating

**Less maintainable:**

```c
int *p = malloc(sizeof(int));
```

**Preferred:**

```c
int *p = malloc(sizeof *p);
```

Both request enough storage for one `int`.

The second form derives the allocation size from the pointed-to type.

Suppose the pointer type changes:

```c
double *p = malloc(sizeof *p);
```

The allocation size automatically follows the declaration.

For arrays:

```c
size_t count = 100;

int *values = malloc(count * sizeof *values);
```

**One additional requirement matters: multiplication must not overflow `size_t`.**

For untrusted or potentially large counts:

```c
#include <stdint.h>
#include <stdlib.h>

int *allocate_array(size_t count) {
    if (count > SIZE_MAX / sizeof(int)) {
        return NULL;
    }

    return malloc(count * sizeof(int));
}
```

This prevents calculating an allocation size smaller than the amount actually required.

## 8. Handle allocation failure

Allocation functions can fail.

**Bad:**

```c
int *p = malloc(sizeof *p);

*p = 42;
```

If `malloc` returns `NULL`, dereferencing `p` is undefined behavior.

**Good:**

```c
int *p = malloc(sizeof *p);

if (p == NULL) {
    // Handle failure
    return;
}

*p = 42;
```

Allocation failure is part of the API contract, not an exceptional condition that the language automatically handles.

## 9. Use `realloc` without losing the original allocation

A classic pointer bug occurs when using `realloc`.

**Bad:**

```c
p = realloc(p, new_size);
```

If allocation fails, `realloc` returns `NULL`, but the original allocation remains valid.

Assigning directly to `p` loses the pointer needed to release that allocation.

**Good:**

```c
void *temp = realloc(p, new_size);

if (temp == NULL) {
    // p still refers to the original allocation
} else {
    p = temp;
}
```

This example assumes `p` is an appropriate allocation pointer and `new_size` is nonzero.

```text
Before realloc:

p ------> [ Original allocation ]


If realloc fails:

p ------> [ Original allocation ]
temp ---> NULL


If realloc succeeds:

temp ---> [ Resized allocation ]

p = temp

p ------> [ Resized allocation ]
```

**On successful reallocation, the old allocation's lifetime ends, even if its storage address remains unchanged.** The returned pointer must be used.

## 10. Prevent dangling pointers and double frees

Consider:

```c
int *p = malloc(sizeof *p);

if (p != NULL) {
    *p = 42;
    free(p);
}
```

After `free`, the allocated object's lifetime has ended.

A common local defensive practice is:

```c
free(p);
p = NULL;
```

This prevents accidental reuse through `p` as an apparently non-null pointer.

However, it does not invalidate other aliases safely:

```c
int *p = malloc(sizeof *p);

if (p != NULL) {
    int *q = p;

    free(p);
    p = NULL;

    // q must not be dereferenced or freed
}
```

```text
Before free:

p -----+
       |
       +----> [ Object ]
       |
q -----+

After free:

p ----> NULL
q       No live allocated object
```

**Setting `p` to `NULL` does not change `q`.**

**Best practice:** Clear ownership and lifetime rules are more important than mechanically setting every pointer to `NULL`.

## 11. Keep pointer arithmetic within valid bounds

Pointer arithmetic is defined relative to array objects.

Consider:

```c
int values[3] = {10, 20, 30};

int *p = values;
```

These expressions are valid:

```text
p + 0
p + 1
p + 2
p + 3
```

The last expression produces a one-past-the-end pointer.

```text
Array object
+----------+----------+----------+
|    10    |    20    |    30    |
+----------+----------+----------+
^          ^          ^          ^
|          |          |          |
p + 0      p + 1      p + 2      p + 3 (one-past)
```

However:

```c
*(p + 3);  // Undefined behavior
p + 4;     // Undefined behavior
```

A one-past pointer can be useful for comparisons or loop termination, but cannot be dereferenced.

Example:

```c
int *current = values;
int *end = values + 3;

while (current != end) {
    printf("%d\n", *current);
    ++current;
}
```

Avoid arbitrary arithmetic on pointers and relational comparisons or subtraction between pointers to unrelated objects.

## 12. Avoid unnecessary casts

C permits conversions between `void *` and pointers to object types.

Therefore, a cast is unnecessary when using `malloc`.

**Avoid:**

```c
int *p = (int *)malloc(sizeof *p);
```

**Prefer:**

```c
int *p = malloc(sizeof *p);
```

The implicit conversion is well-defined in C.

More importantly, avoid casting pointers merely to bypass type incompatibilities.

For example:

```c
float x = 3.14f;
int *p = (int *)&x;
```

Dereferencing `p` to read `x` as an `int` generally violates C's effective-type access rules.

When examining object representations, character-type access is a special permitted mechanism. `memcpy` is often the clearest portable choice for copying representations into appropriately typed objects.

**Pointer casts do not make an otherwise invalid memory access safe.**

## 13. Prefer simple pointer interfaces

Compare two approaches.

**Complex interface:**

```c
void compute(int **result);
```

**Simpler interface:**

```c
int compute(void);
```

If a function only computes an integer, returning the value directly avoids unnecessary pointer manipulation.

Pointer output parameters remain useful when a function must return multiple results or report errors separately.

For example:

```c
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>

bool divide(int numerator, int denominator, int *result) {
    if (result == NULL || denominator == 0) {
        return false;
    }

    if (numerator == INT_MIN && denominator == -1) {
        return false;
    }

    *result = numerator / denominator;

    return true;
}
```

Here the pointer is justified: it enables a result to be written while the function returns a success indicator.

## 14. Use `restrict` only when aliasing guarantees are valid

For performance-sensitive code, C provides the `restrict` qualifier.

Consider:

```c
void add(size_t n, int *restrict dst, const int *restrict a, const int *restrict b) {
    for (size_t i = 0; i < n; ++i) {
        dst[i] = a[i] + b[i];
    }
}
```

`restrict` communicates aliasing constraints that can enable compiler optimizations.

It is not a request to the compiler to assume arbitrary memory safety.

The function's caller must satisfy the applicable `restrict` rules. In particular, modifying elements through `dst` while also accessing those elements through an independent restricted input path can violate the contract.

Incorrect use can produce undefined behavior.

**Best practice:** Introduce `restrict` when its aliasing guarantees are proven, rather than adding it indiscriminately.

## Pointer design principles

| Principle                                  | Rationale                                    |
| ------------------------------------------ | -------------------------------------------- |
| Initialize pointers                        | Avoid indeterminate pointer values           |
| Make ownership explicit                    | Prevent leaks and double frees               |
| Respect lifetimes                          | Prevent dangling-pointer accesses            |
| Carry array lengths                        | Make bounds available                        |
| Prefer `const` for read-only access        | Express mutation restrictions                |
| Check allocation results                   | Handle memory exhaustion                     |
| Use temporary pointers with `realloc`      | Preserve allocations on failure              |
| Avoid unnecessary casts                    | Preserve type checking                       |
| Minimize pointer arithmetic                | Reduce bounds-related defects                |
| Prefer values over pointers when practical | Reduce indirection and lifetime dependencies |

## 15. A complete example: safe dynamic array

```c
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

struct IntArray {
    int *data;
    size_t length;
};

bool array_create(struct IntArray *array, size_t length) {
    if (array == NULL) {
        return false;
    }

    array->data = NULL;
    array->length = 0;

    if (length == 0) {
        return true;
    }

    if (length > SIZE_MAX / sizeof *array->data) {
        return false;
    }

    int *data = malloc(length * sizeof *data);

    if (data == NULL) {
        return false;
    }

    array->data = data;
    array->length = length;

    return true;
}

void array_destroy(struct IntArray *array) {
    if (array == NULL) {
        return;
    }

    free(array->data);

    array->data = NULL;
    array->length = 0;
}
```

Usage:

```c
int main(void) {
    struct IntArray array = {0};

    if (!array_create(&array, 100)) {
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < array.length; ++i) {
        array.data[i] = (int)i;
    }

    array_destroy(&array);

    return EXIT_SUCCESS;
}
```

**Call `array_create` on a fresh `IntArray` or one that has already been destroyed.** The instance exclusively owns its allocation, so avoid shallow copies while it owns storage.

It illustrates several principles:

- The pointer starts in a known state.
- The length accompanies the pointer.
- Allocation size overflow is checked.
- Allocation failure is handled.
- Ownership belongs to the array abstraction.
- Destruction releases the allocation and resets the structure.

Its ownership model is:

```text
+-----------------------+
| IntArray              |
| data                  |
| length = 100          |
+-----------------------+
            | owns
            v
+-----------------------+
| int[100]              |
| Dynamically allocated |
+-----------------------+
            |
            v
+-----------------------+
| array_destroy()       |
+-----------------------+
            |
            v
+-----------------------+
| Allocation released   |
+-----------------------+
```

## The fundamental engineering rule

A pointer's declaration alone does not establish that it is safe to dereference.

A safe pointer access requires a valid relationship between several properties:

```text
Pointer access
|
+-- Type
+-- Lifetime
+-- Bounds
+-- Alignment
|
v
Valid access
```

For dynamic memory, the owner releases the allocation once it is no longer needed and all permitted accesses have finished.

**The most reliable pointer-based C code minimizes the number of places where pointer validity, object lifetime, and ownership must be reasoned about simultaneously.**

Keeping pointer operations localized, passing explicit bounds, and designing clear ownership contracts usually provides more safety than scattered null checks alone.
