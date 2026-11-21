# Pass by value

In C, **function arguments are passed by value**.

This means that when a function is called, the value of each argument is used to initialize the corresponding parameter.

The parameter is a **separate object** from the object in the calling function.

**Consequently, modifying a parameter does not modify the caller's original object.**

## 1. Understanding pass by value

Consider:

```c
#include <stdio.h>

void increment(int x) {
    x = x + 1;
}

int main(void) {
    int number = 10;

    increment(number);

    printf("%d\n", number);
}
```

Output:

```text
10
```

Why doesn't `number` become `11`?

When `increment(number)` executes, the value stored in `number` is passed to the function.

The parameter `x` is initialized with that value.

Conceptually:

```text
main()                                    increment()
+--------------------+                    +--------------------+
| number = 10        | --- copy --------> | x = 10             |
+--------------------+                    +--------------------+
```

After executing `x = x + 1`:

```text
main()                                    increment()
+--------------------+                    +--------------------+
| number = 10        |                    | x = 11             |
+--------------------+                    +--------------------+
```

There are two distinct objects:

- **`number`:** An object in `main`.
- **`x`:** A parameter object in `increment`.

**Changing `x` does not change `number`.**

**The value is transferred, not the identity of the object.**

## 2. Parameters are objects

Consider:

```c
void process(int x) {
    x = 100;
}
```

The parameter `x` is an object with automatic storage duration.

Its lifetime is associated with the function invocation.

**Each call creates a distinct parameter object:**

```c
process(10);
process(20);
process(30);
```

Conceptually:

```text
+--------------------+
| Call 1             |
| x = 10             |
+--------------------+
          |
          v
+--------------------+
| Function returns   |
| x lifetime ends    |
+--------------------+

+--------------------+
| Call 2             |
| x = 20             |
+--------------------+
          |
          v
+--------------------+
| Function returns   |
| x lifetime ends    |
+--------------------+

+--------------------+
| Call 3             |
| x = 30             |
+--------------------+
          |
          v
+--------------------+
| Function returns   |
| x lifetime ends    |
+--------------------+
```

Recursive calls likewise have distinct parameter instances.

## 3. Passing a pointer is still pass by value

This is one of the most important concepts in C.

Consider:

```c
void increment(int *p) {
    *p = *p + 1;
}

int main(void) {
    int number = 10;

    increment(&number);
}
```

After the call, `number == 11`.

Does this mean C supports pass by reference?

**No. C still passes the argument by value.**

The difference is that the argument's value is now an address.

Conceptually, assuming `number` resides at address `0x1000`:

```text
main()                                    increment()
+--------------------+                    +--------------------+
| number = 10        | <----------------- | p = 0x1000         |
| Address: 0x1000    |                    |                    |
+--------------------+                    +--------------------+
```

**The parameter `p` is a separate pointer object.**

Its stored value is the address of `number`.

When the function evaluates:

```c
*p = *p + 1;
```

It accesses the object at that address.

Therefore, the original `number` object is modified.

The distinction is:

- **`p` is a copy of the pointer value.**
- **`*p` designates the original object.**

### Modifying the pointer versus modifying the pointee

Consider:

```c
void change(int *p) {
    int local = 100;

    p = &local;
    *p = 200;
}

int main(void) {
    int number = 10;

    change(&number);
}
```

After the function returns, `number` is still `10`.

Why?

Because `p = &local` changes the pointer parameter itself, not the caller's object.

```text
Initially:

main()                                    change()
+--------------------+                    +--------------------+
| number = 10        | <----------------- | p = &number        |
+--------------------+                    +--------------------+

After p = &local and *p = 200:

main()                                    change()
+--------------------+                    +--------------------+
| number = 10        |                    | p = &local         |
+--------------------+                    +--------------------+
                                                    |
                                                    v
                                          +--------------------+
                                          | local = 200        |
                                          +--------------------+
```

**The original pointer value was copied into `p`, but subsequent assignments to `p` affect only that parameter object.**

## 4. Structures are also passed by value

Pass by value applies to structures, not just scalar values.

Consider:

```c
struct Point {
    int x;
    int y;
};

void move(struct Point p) {
    p.x += 10;
    p.y += 10;
}

int main(void) {
    struct Point point = {1, 2};

    move(point);
}
```

After `move(point)`, the caller's `point` still contains `{1, 2}`.

Conceptually:

```text
Caller                                    Callee
+--------------------+                    +--------------------+
| point              |                    | p                  |
| x = 1              | --- copy --------> | x = 1              |
| y = 2              |                    | y = 2              |
+--------------------+                    +--------------------+
                                                    |
                                                    v
                                          +--------------------+
                                          | After move:        |
                                          | x = 11             |
                                          | y = 12             |
                                          +--------------------+
```

**A structure parameter is a distinct structure object initialized from the argument's value.**

This has performance implications: passing a large structure by value may require copying its contents, although the compiler is free to optimize the physical implementation.

For example:

```c
struct Large {
    char data[4096];
};

void process(struct Large value);
```

Passing `struct Large` by value has value-copy semantics.

An alternative is to pass a pointer:

```c
void process(const struct Large *value);
```

This avoids requiring an independent structure parameter, but changes the semantics: the function now receives an address through which it can inspect the original structure.

The `const` qualification prevents modification through that pointer, subject to C's usual qualification rules.

## 5. Arrays are different: parameter adjustment

Consider:

```c
void modify(int values[3]) {
    values[0] = 100;
}

int main(void) {
    int numbers[3] = {1, 2, 3};

    modify(numbers);
}
```

After the call:

```text
numbers = {100, 2, 3}
```

At first glance, this seems to contradict pass by value.

But it does not.

**In a function parameter declaration, an array type is adjusted to a pointer type.**

These declarations specify the same parameter type:

```c
void modify(int values[3]);
void modify(int *values);
```

When `modify(numbers)` is called, the array expression `numbers` normally undergoes array-to-pointer conversion.

The function receives a pointer to the first element.

```text
Caller                    Callee

numbers                   values
+-----+-----+-----+       +----------+
|  1  |  2  |  3  |       | address  |
+-----+-----+-----+       +----------+
   ^                           |
   |  values[0]                |
   +---------------------------+
```

The array itself is not copied.

**Instead, a pointer value is passed by value.**

This explains why changing `values[0]` changes `numbers[0]`.

It also explains why `sizeof(values)` inside this function gives the size of a pointer, rather than the size of the original array.

## 6. Returning a value

Pass by value also helps explain function return values.

Consider:

```c
int increment(int x) {
    x++;
    return x;
}

int main(void) {
    int number = 10;

    number = increment(number);
}
```

The execution is conceptually:

```text
Caller                                    Callee
+--------------------+                    +--------------------+
| number = 10        | - Pass value 10 -> | x = 10             |
+--------------------+                    +--------------------+
                                                    |
                                                    v
+--------------------+                    +--------------------+
| number = 11        | <- Return value 11 | x = 11             |
+--------------------+                    +--------------------+
```

**The caller changes `number` through its own assignment.**

The callee does not directly modify the caller's object.

This style is often preferable for small, self-contained computations.

## 7. Pass by value versus pass by reference

C does not have a built-in pass-by-reference parameter mechanism like C++ references.

However, pointers allow a function to indirectly modify an object in the caller.

| Property                                                     | Passing an `int`            | Passing an `int *`         |
| ------------------------------------------------------------ | --------------------------- | -------------------------- |
| What is passed?                                              | Integer value               | Pointer value              |
| Parameter is a new object?                                   | Yes                         | Yes                        |
| Can assigning to the parameter change the caller's variable? | No                          | No                         |
| Can the callee modify the caller's integer?                  | Not through the value alone | Yes, through dereferencing |
| Does C still use pass by value?                              | Yes                         | Yes                        |

## Fundamental mental model

```text
                  Function call
                        |
                        v
                Evaluate argument
                        |
                        v
                 Obtain a value
                        |
                        v
              Initialize parameter
                        |
                        v
            Separate parameter object
                        |
      +-----------------+-----------------+
      |                                   |
      v                                   v
Integer value                       Pointer value
      |                                   |
      v                                   v
Modify local                         Dereference
  parameter                            pointer
      |                                   |
      v                                   v
Caller object                        May access
  unchanged                         caller object
```

The essential principle is:

**C always passes argument values to functions, never caller objects themselves.**

When the argument is an integer, the parameter receives an integer value. When the argument is a pointer, the parameter receives a pointer value. When the argument is a structure, the parameter receives a structure value.

The ability to modify caller-owned objects through pointers is a consequence of **indirection**, not a different argument-passing mechanism.
