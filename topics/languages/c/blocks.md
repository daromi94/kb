# Blocks

In C, a **block** is a syntactic construct that groups declarations and statements into a single unit.

A block is written using curly braces `{}` and is formally called a _compound statement_.

A compound statement allows a sequence of block items to appear wherever a single statement is permitted.

```c
{
    int x = 10;
    int y = 20;

    int result = x + y;
}
```

The braces delimit the block. The declarations and statements inside them are its **block items**.

A block is important for three reasons:

- It groups statements into a single syntactic unit.
- It establishes a scope for identifiers declared inside it.
- It affects the lifetime of objects with automatic storage duration.

## 1. Blocks group statements

Consider:

```c
if (condition) {
    int x = 10;
    x++;
    printf("%d\n", x);
}
```

An `if` statement controls the execution of one statement.

**Because a block is itself a statement, it allows multiple declarations and statements to be grouped together.**

```text
   if (condition)
          |
          v
+------------------+
| Block            |
|                  |
| int x = 10;      |
| x++;             |
| printf(...);     |
+------------------+
```

A block can appear on its own inside a function:

```c
int main(void) {
    int x = 10;

    {
        int y = 20;
        x += y;
    }

    return 0;
}
```

The inner block is a valid compound statement.

## 2. Blocks establish scope

One of the most important properties of blocks is **block scope**.

**Scope determines where an identifier can be used to refer to the entity it denotes.**

Consider:

```c
void example(void) {
    int x = 10;

    {
        int y = 20;

        x = x + y;
    }

    x++;

    // y is not visible here
}
```

The identifier `x` belongs to the outer block.

The identifier `y` belongs to the inner block.

```text
+-------------------------------------+
| Outer block                         |
|                                     |
| int x = 10;                         |
|                                     |
|    +--------------------------+     |
|    | Inner block              |     |
|    |                          |     |
|    | int y = 20;              |     |
|    |                          |     |
|    | x = x + y;               |     |
|    +--------------------------+     |
|                                     |
| x++;                                |
|                                     |
| // y is out of scope                |
+-------------------------------------+
```

**Identifiers declared in an outer scope are generally accessible inside nested blocks unless hidden by another declaration.**

**However, identifiers declared in an inner block are not accessible outside their scope.**

Strictly speaking, the scope of an ordinary block-scope identifier starts just after the completion of its declarator and ends at the end of the enclosing block.

## 3. Blocks and object lifetime

Blocks are closely related to objects with **automatic storage duration**.

Consider:

```c
void example(void) {
    int x = 10;

    {
        int y = 20;
    }
}
```

Both `x` and `y` have automatic storage duration.

Their lifetimes are associated with execution of their respective blocks.

```text
  Execution enters example()
               |
               v
+-----------------------------+
| Outer block begins          |
|                             |
| Object x lifetime begins    |
|                             |
|   +---------------------+   |
|   | Inner block begins  |   |
|   |                     |   |
|   | Object y exists     |   |
|   |                     |   |
|   | Inner block ends    |   |
|   +---------------------+   |
|                             |
| Object y no longer exists   |
|                             |
| Outer block ends            |
+-----------------------------+
               |
               v
    Object x lifetime ends
```

**For ordinary automatic objects, storage remains available until execution of the associated block ends.**

Compiler optimizations mean this does not necessarily correspond to actual stack allocations and deallocations.

### An important exception: static storage duration

**A variable declared inside a block does not necessarily have automatic storage duration.**

```c
void counter(void) {
    static int count = 0;

    count++;
}
```

Although `count` has block scope, it has static storage duration.

**Its object exists for the entire execution of the program.**

This establishes an important principle:

**Scope controls the visibility of a name. Storage duration controls the existence of an object.**

They are independent properties.

## 4. Nested blocks and shadowing

A nested block may declare an identifier with the same spelling as an identifier in an enclosing scope.

```c
#include <stdio.h>

int main(void) {
    int x = 10;

    {
        int x = 20;

        printf("%d\n", x);
    }

    printf("%d\n", x);
}
```

Output:

```text
20
10
```

There are two distinct objects.

```text
+--------------------------------+
| Outer block                    |
|                                |
| x -----------------> [10]      |
|                                |
|   +------------------------+   |
|   | Inner block            |   |
|   |                        |   |
|   | x -----------> [20]    |   |
|   |                        |   |
|   | Outer x is hidden      |   |
|   +------------------------+   |
|                                |
| x refers to outer object       |
+--------------------------------+
```

**The inner declaration hides the outer declaration until the inner block ends.**

This behavior is called **name hiding** or _shadowing_.

**It does not modify or replace the outer object.**

## 5. A block is not necessarily a new stack frame

A common misconception is that every block allocates a new stack frame.

Consider:

```c
void example(void) {
    int x = 10;

    {
        int y = 20;
        x += y;
    }
}
```

At the language level, the inner block introduces a distinct scope and controls the lifetime of `y`.

However, the compiler is not required to create a separate stack frame for the inner block.

Conceptually, a compiler might organize storage as:

```text
Typical function stack frame
+-------------------------+
| Return address          |
+-------------------------+
| Saved registers         |
+-------------------------+
| Object x (if stored)    |
+-------------------------+
| Object y (if stored)    |
+-------------------------+
```

Or it might optimize `y` away entirely.

The **block is a language-level construct**, not a mandatory runtime memory structure.

## 6. Blocks and control flow

Blocks interact with control-flow statements such as `if`, `while`, and `for`.

Consider:

```c
for (int i = 0; i < 3; i++) {
    int x = i * 10;
}
```

The block is entered once per iteration.

For `x`, each iteration corresponds to a new execution of its associated block, and its automatic lifetime ends when that iteration exits the block.

```text
Iteration 0
     |
     v
Enter block
     |
     v
   x = 0
     |
     v
Exit block

Iteration 1
     |
     v
Enter block
     |
     v
  x = 10
     |
     v
Exit block

Iteration 2
     |
     v
Enter block
     |
     v
  x = 20
     |
     v
Exit block
```

An important subtlety is that a `for` loop can also introduce a scope for variables declared in its initialization clause.

**The scope of `i` extends through the loop, including its body, but not beyond the loop statement.**

## 7. Block versus function

A function definition contains a function body written as a compound statement.

```c
void example(void) {
    int x = 10;
}
```

However, a block and a function are not the same concept.

| Property                   | Block | Function                                               |
| -------------------------- | ----- | ------------------------------------------------------ |
| Groups statements          | Yes   | Yes, through its body                                  |
| Introduces a scope         | Yes   | Function body has block scope                          |
| Can be nested              | Yes   | Portable C does not permit nested function definitions |
| Can be called              | No    | Yes                                                    |
| Has parameters             | No    | Yes                                                    |
| Requires a new stack frame | No    | Not guaranteed                                         |

**A function defines callable behavior. A block is a statement that groups declarations and other statements.**

## The fundamental mental model

```text
                     Block
                       |
     +-----------------+-----------------+
     |                 |                 |
     v                 v                 v
  Syntax             Scope           Execution
     |                 |                 |
     v                 v                 v
  Groups           Controls           Affects
statements        identifier         automatic
                  visibility         lifetimes
```

A block is a **lexical and execution boundary** in C.

It groups declarations and statements, defines where identifiers are visible, and helps determine how long automatic objects exist.

The key distinction is that **a block governs both source-code structure and aspects of runtime behavior, but it does not necessarily correspond to a physical region of memory or a stack frame.**
