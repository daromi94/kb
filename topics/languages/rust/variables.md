# Variables

A **variable** in Rust is a named binding to a value. Variables allow programs to store data, reference it, and manipulate it.

Rust variables have several important characteristics:

- Variables are **immutable by default**.
- Mutability must be explicitly declared using `mut`.
- Variables have types, often inferred by the compiler.
- Variables follow lexical scope rules.
- Variables participate in Rust's ownership and borrowing system.
- Rust supports _shadowing_, which creates a new binding with an existing name.

These characteristics are central to Rust's approach to memory safety and predictable program behavior.

## 1. Declaring variables with `let`

Variables are declared using the `let` keyword.

```rust
fn main() {
    let x = 10;
    let name = "Rust";
    let enabled = true;
}
```

The general syntax is:

```rust
let variable_name = expression;
```

**Every variable has a type, even when that type is not written explicitly.**

```rust
let x = 10;          // i32
let enabled = true;  // bool
let name = "Rust";   // &str
```

Rust uses **type inference** to determine variable types from their initialization and usage.

Types can also be declared explicitly:

```rust
let x: i64 = 10;
let temperature: f64 = 36.5;
```

Unlike dynamically typed languages, Rust determines types during compilation.

```text
  let x = 10;
       |
       v
Type Inference
       |
       v
    x: i32
       |
       v
 Compile-time
 Type Checking
```

**Once established, the type of a binding cannot change.**

## 2. Immutability by default

Consider:

```rust
fn main() {
    let x = 10;

    x = 20;
}
```

This produces a compilation error:

```text
error[E0384]: cannot assign twice to immutable variable `x`
```

The binding `x` is immutable.

Conceptually:

```text
 let x = 10
      |
      v
+-----------+
|  x = 10   |
+-----------+
      |
      | Assignment to x
      v
  Rejected
```

To allow reassignment, the variable must be declared mutable.

```rust
fn main() {
    let mut x = 10;

    x = 20;

    println!("{x}");
}
```

Output:

```text
20
```

**`mut`** tells the compiler that the binding permits mutation under Rust's ownership and borrowing rules.

### Why immutable by default?

Immutability reduces the number of possible state transitions in a program.

Consider:

```rust
let mut balance = 100;

balance += 50;
balance -= 20;
balance *= 2;
```

The value of `balance` changes several times.

In contrast:

```rust
let balance = 100;
```

The binding cannot be reassigned, and a plain integer value cannot be mutated through it.

This makes code easier to reason about, particularly when multiple functions, threads, and ownership boundaries are involved.

**Important:** **An immutable binding does not necessarily make all referenced data immutable.** Types with interior mutability, such as `Cell<T>` and `Mutex<T>`, can allow mutation through an immutable binding.

## 3. Shadowing

Rust allows a new variable to reuse the name of a previous variable.

This is called **shadowing**.

```rust
fn main() {
    let x = 10;

    let x = x + 5;

    let x = x * 2;

    println!("{x}");
}
```

Output:

```text
30
```

**Each `let` creates a new binding.**

```text
 let x = 10
      |
      v
   x1: 10
      |
      v
let x = x + 5
      |
      v
   x2: 15
      |
      v
let x = x * 2
      |
      v
   x3: 30
```

Although the source code uses the same name, these are distinct bindings.

This is different from mutation:

```rust
let mut x = 10;
x = 15;
```

**Mutation changes the value associated with an existing binding.**

**Shadowing creates a new binding that hides the previous one.**

### Shadowing can change types

```rust
fn main() {
    let value = "123";

    let value = value.parse::<i32>().unwrap();

    println!("{}", value + 10);
}
```

The first `value` has type `&str`.

The second `value` has type `i32`.

```text
value: &str
     |
     | Parse
     v
value: i32
```

This is useful for transformations in which a value progresses through several representations.

For example:

```rust
let input = "42";
let input = input.parse::<i32>().unwrap();
let input = input * 2;
```

The identifier remains meaningful without requiring names like `input_string`, `input_integer`, and `input_doubled`.

## 4. Variable scope

**Variables are valid only within their scope.**

Rust uses lexical scoping, typically defined by curly braces.

```rust
fn main() {
    let x = 10;

    {
        let y = 20;

        println!("{x}");
        println!("{y}");
    }

    println!("{x}");

    // println!("{y}"); // Error
}
```

The variable `y` exists only inside the inner block.

```text
             main()
                |
                v
+--------------------------------+
|                                |
|  x = 10                        |
|                                |
|  +--------------------------+  |
|  |                          |  |
|  | y = 20                   |  |
|  |                          |  |
|  | x and y accessible       |  |
|  |                          |  |
|  +--------------------------+  |
|                                |
|  Only x accessible             |
|                                |
+--------------------------------+
```

Scope also interacts with resource management.

When an owned value leaves its scope, Rust normally invokes its destructor, `Drop::drop`, and releases its owned resources.

```rust
fn main() {
    {
        let text = String::from("hello");

        println!("{text}");
    } // text is dropped here

    println!("Finished");
}
```

For `String`, dropping releases its heap allocation.

This connects variable scope directly to deterministic resource cleanup.

## 5. Variables and ownership

One of Rust's most important distinctions is that variables are not merely names for values.

They also participate in **ownership**.

Consider:

```rust
fn main() {
    let a = String::from("hello");

    let b = a;

    println!("{b}");
}
```

A `String` owns heap-allocated memory.

Initially:

```text
    Stack                    Heap

+------------+          +-------------+
| a: String  |--------->| "hello"     |
+------------+          +-------------+
```

After:

```rust
let b = a;
```

**Ownership moves from `a` to `b`.**

```text
    Stack                    Heap

+------------+
| a: moved   |
+------------+

+------------+          +-------------+
| b: String  |--------->| "hello"     |
+------------+          +-------------+
```

The original binding `a` can no longer be used as a `String`.

```rust
println!("{a}"); // Compile-time error
```

This prevents both variables from independently destroying the same allocation.

The actual stack representation of `String` includes a pointer, length, and capacity. **A move transfers those fields conceptually; it does not copy the heap contents.**

### What about integers?

```rust
let a = 10;
let b = a;

println!("{a}");
println!("{b}");
```

This works because `i32` implements `Copy`.

```text
a: 10
  |
  | Copy
  v
b: 10
```

Both variables remain valid, and each holds an independent integer value.

**The distinction between `Copy` and move semantics is fundamental to Rust.**

## 6. Variables and borrowing

Access to a value can be temporarily shared through references.

```rust
fn main() {
    let text = String::from("hello");

    let reference = &text;

    println!("{reference}");
    println!("{text}");
}
```

Here, `reference` borrows `text`.

```text
     text
       |
       v
+-------------+
|   String    |-------> Heap allocation
+-------------+
       ^
       |
       |
   reference
    &String
```

**The reference does not own the string.**

**An immutable reference `&T` permits shared access without transferring ownership.**

**A mutable reference `&mut T` permits modification under exclusive-access rules:**

```rust
fn main() {
    let mut text = String::from("hello");

    let reference = &mut text;

    reference.push_str(" world");

    println!("{text}");
}
```

**Rust's borrow checker ensures that conflicting accesses do not overlap.**

This is where variables become closely connected to Rust's memory-safety guarantees.

## 7. Uninitialized variables

Rust permits declaring a variable without immediately initializing it:

```rust
fn main() {
    let x: i32;

    x = 42;

    println!("{x}");
}
```

**However, reading a variable before initialization is forbidden.**

```rust
fn main() {
    let x: i32;

    println!("{x}"); // Compile-time error
}
```

Rust performs definite-initialization analysis to ensure a variable has a valid value before it is read.

**An uninitialized declaration can still be immutable because initialization is not considered reassignment.**

## 8. Variables vs. constants vs. statics

Rust distinguishes local variables from `const` and `static` items.

| Feature        | `let`                             | `const`                          | `static`                    |
| -------------- | --------------------------------- | -------------------------------- | --------------------------- |
| Purpose        | Local binding                     | Compile-time constant value      | Fixed storage location      |
| Mutability     | Optional `mut`                    | Immutable                        | Immutable by default        |
| Type inference | Yes                               | Explicit type required           | Explicit type required      |
| Scope          | Local lexical binding             | Item scope                       | Item scope                  |
| Memory         | Depends on value and optimization | Not guaranteed dedicated storage | Has a fixed memory location |

Examples:

```rust
let count = 10;

const MAX_CONNECTIONS: usize = 100;

static REQUEST_COUNT: AtomicUsize = AtomicUsize::new(0);
```

**`const`** defines a value that can be evaluated at compile time. Its uses do not necessarily refer to one shared memory location.

**`static`** defines a value with a fixed memory location that lives for the entire program.

For mutable global state, safe Rust generally uses synchronization primitives such as atomics, mutexes, or locks.

## 9. Important distinction: a variable is not necessarily a stack allocation

A common misconception is:

> Every Rust variable is stored on the stack.

This is incorrect.

Consider:

```rust
let number = 42;
let text = String::from("hello");
let boxed = Box::new(100);
```

Conceptually:

```text
            Stack                              Heap
+----------------------------+            +-------------+
| number: 42                 |            |             |
|                            |            |             |
| text: String metadata -----+----------->| "hello"     |
|                            |            |             |
| boxed: Box pointer --------+----------->| 100         |
+----------------------------+            +-------------+
```

The `String` value contains metadata that refers to heap storage.

The `Box<i32>` owns an integer allocated on the heap.

Furthermore, compiler optimization may eliminate stack allocations entirely or keep values in CPU registers.

**Rust variables are language-level bindings. Their physical storage locations are implementation and optimization details.**

**Key takeaway:** Variables in Rust are typed bindings with explicit mutability, lexical scope, and ownership semantics. These rules enable the compiler to reason about how values are accessed, modified, moved, and destroyed before the program executes.
