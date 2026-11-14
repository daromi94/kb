# Ownership

**Ownership is Rust's mechanism for managing resources and ensuring memory safety without requiring a garbage collector.**

The central idea is simple: every value has an owner, and the compiler tracks how ownership moves, how values are borrowed, and when resources must be released.

Ownership provides three important guarantees:

- **Memory safety:** Prevents use-after-free and double-free errors in safe Rust.
- **Deterministic resource management:** Resources are normally released when their owners leave scope.
- **Zero-cost abstraction:** Most ownership checks happen at compile time, without requiring runtime ownership tracking.

## 1. The problem ownership solves

Consider a program that allocates memory dynamically.

```text
    Program
       |
       v
Allocate Memory
       |
       v
  Use Memory
       |
       v
  Free Memory
```

The difficult part is determining **who is responsible for releasing the allocation and when it is safe to do so**.

In languages with manual memory management, incorrect resource handling can introduce serious problems.

### Use-after-free

```text
 Allocate memory
        |
        v
    pointer A
        |
        v
   Free memory
        |
        v
Access pointer A
        |
        v
 USE-AFTER-FREE
```

The program attempts to access memory that is no longer valid.

### Double-free

```text
    Allocate memory
           |
           v
       pointer A
           |
   +-------+-------+
   |               |
   v               v
Free A          Free A
   |               |
   +-------X-------+
           |
      DOUBLE-FREE
```

### Memory leaks

Memory is allocated but never released, even when the program no longer needs it.

Garbage-collected languages address many of these problems through runtime reachability analysis.

Rust instead uses ownership and borrowing rules enforced primarily during compilation.

## 2. The three fundamental rules

Rust's ownership model is commonly introduced through three rules:

1. **Each value in Rust has an owner.**
2. **There can be only one owner at a time.**
3. **When the owner goes out of scope, the value is dropped.**

These rules describe Rust's ordinary single-owner model. Types such as `Rc<T>` and `Arc<T>` support shared ownership of an underlying allocation through reference counting.

Consider:

```rust
fn main() {
    let text = String::from("hello");

    println!("{text}");
}
```

The binding `text` owns the `String`.

```text
      Stack                             Heap
+----------------+
| text: String   |                +----------------+
|                |                |                |
| ptr -----------+--------------->| h e l l o      |
| len = 5        |                |                |
| capacity = 5   |                +----------------+
+----------------+
```

Conceptually, `String` contains:

- A pointer to its heap allocation.
- The number of initialized bytes.
- The allocation's capacity.

**The exact layout of these fields is not guaranteed by Rust's stable language specification.**

When `text` goes out of scope, Rust calls its destructor, which releases the owned allocation.

```text
  Enter scope
       |
       v
 Create String
       |
       v
  Use String
       |
       v
  Leave scope
       |
       v
  Drop String
       |
       v
Free allocation
```

No garbage collector needs to discover that the allocation is unreachable.

## 3. Ownership transfer: move semantics

Consider:

```rust
fn main() {
    let a = String::from("hello");

    let b = a;

    println!("{b}");
}
```

The assignment `let b = a` **moves ownership** from `a` to `b`.

**It does not clone the underlying string.**

Before the assignment:

```text
     Stack                     Heap

+-------------+            +-----------+
| a: String   |----------->| "hello"   |
+-------------+            +-----------+
```

After the assignment:

```text
     Stack                     Heap

+-------------+
| a: moved    |
+-------------+

+-------------+            +-----------+
| b: String   |----------->| "hello"   |
+-------------+            +-----------+
```

**The old binding `a` is no longer valid for accessing that string.**

This code fails:

```rust
let a = String::from("hello");
let b = a;

println!("{a}"); // Error: borrow of moved value
```

### Why?

Without move semantics, both variables might independently believe they own the same allocation.

```text
a --------+
          |
          v
      Heap Data
          ^
          |
b --------+
```

If both owners attempted to release it, a double-free could occur.

Rust avoids that situation by invalidating the original binding after the move.

**A move changes which binding owns a resource, not necessarily where the resource resides in memory.**

## 4. Move does not necessarily mean copying heap data

A common misconception is that moving a value requires copying all of its contents.

For `String`, the move conceptually transfers its pointer, length, and capacity.

```text
Before move

a
+-----------+
| ptr ------+--------> Heap allocation
| len = 5   |
| cap = 5   |
+-----------+

      |
      | Move
      v

After move

b
+-----------+
| ptr ------+--------> Same heap allocation
| len = 5   |
| cap = 5   |
+-----------+
```

**The heap bytes are not duplicated.**

However, the compiler may still need to copy the value's inline representation, depending on the circumstances.

For large values stored inline, a move can involve copying substantial data. **Rust does not guarantee that every move is a constant-time operation.**

## 5. Ownership and the `Copy` trait

Not all assignments invalidate the original variable.

Consider:

```rust
fn main() {
    let a = 10;
    let b = a;

    println!("{a}");
    println!("{b}");
}
```

Both bindings remain valid.

Why?

Because `i32` implements the `Copy` trait.

**For `Copy` types, assignments create an independent copy.**

```text
       a: 10
         |
         | Copy
         v
       b: 10

Both remain valid.
```

Common `Copy` types include integers, floating-point types, booleans, characters, and shared references.

**A type can implement `Copy` only when its fields support copying and the type does not implement `Drop`.**

### `Copy` vs. `Clone`

| Property                       | `Copy`   | `Clone`                          |
| ------------------------------ | -------- | -------------------------------- |
| Invocation                     | Implicit | Explicit `.clone()`              |
| Can duplicate heap allocations | No       | Yes, depending on implementation |
| Can implement `Drop`           | No       | Yes                              |
| May involve custom logic       | No       | Yes                              |
| Original remains valid         | Yes      | Yes                              |

For example:

```rust
let a = String::from("hello");
let b = a.clone();
```

Now two independent strings exist:

```text
a ----------------> Heap A: "hello"

b ----------------> Heap B: "hello"
```

Cloning a `String` requires allocating and copying its string data.

## 6. Ownership and function calls

Ownership rules also apply to function parameters.

```rust
fn consume(value: String) {
    println!("{value}");
}

fn main() {
    let text = String::from("hello");

    consume(text);

    // println!("{text}"); // Error
}
```

**Passing `text` by value moves its ownership into the function.**

```text
   main()                         consume()
      |                               |
text: String                          |
      |                               |
      +------------ move ------------>|
                                      |
                                value: String
                                      |
                                      v
                                  println()
                                      |
                                      v
                                 Drop value
```

When `consume` returns, `value` is dropped.

The string allocation is released.

### Returning ownership

A function can transfer ownership back to its caller.

```rust
fn transform(mut value: String) -> String {
    value.push_str(" world");
    value
}

fn main() {
    let text = String::from("hello");

    let text = transform(text);

    println!("{text}");
}
```

The ownership sequence is:

```text
  main()
     |
     | owns String
     |
     v
transform()
     |
     | owns String
     |
     v
  return
     |
     | ownership transferred
     v
  main()
     |
     v
   Drop
```

**Ownership can move through many functions, but only the current owner is responsible for the value.**

## 7. Borrowing: accessing values without taking ownership

Moving a value into every function would be inconvenient.

Rust solves this through borrowing.

**A reference provides temporary access to a value without transferring ownership.**

```rust
fn print_length(value: &String) {
    println!("{}", value.len());
}

fn main() {
    let text = String::from("hello");

    print_length(&text);

    println!("{text}");
}
```

The ownership relationship remains unchanged.

```text
   main()
      |
      v
text: String <------- borrows -------- value: &String
      |                                       |
      | owns                                  v
      v                                print_length()
  Heap Data
```

**There is still one owner: `text`.**

The function only borrows access to its contents.

### The borrowing rules

For ordinary Rust references, the central rule is:

**At a given time, access to the same value can be shared for reading or exclusive for mutation.**

```text
   Shared access

       Value
         |
   +-----+-----+
   |           |
   v           v
  &T          &T

      Allowed


 Exclusive access

       Value
         |
         v
      &mut T

      Allowed


Conflicting access

       Value
         |
   +-----+-----+
   |           |
   v           v
  &T        &mut T

     Rejected
```

This is often summarized as _aliasing XOR mutability_.

Rust can permit separate mutable borrows of non-overlapping portions of a value.

## 8. Ownership and lifetimes

**References cannot outlive the values they borrow.**

Consider:

```rust
fn main() {
    let reference;

    {
        let text = String::from("hello");
        reference = &text;
    }

    println!("{reference}");
}
```

This does not compile.

```text
      Outer scope
+----------------------+
|                      |
|  reference           |
|      |               |
|      v               |
|  +---------------+   |
|  | Inner scope   |   |
|  |               |   |
|  | text: String  |   |
|  +---------------+   |
|      |               |
|      v               |
|  text dropped        |
|      |               |
|      v               |
|  reference invalid   |
|                      |
+----------------------+
```

The borrowed `String` is destroyed when the inner scope ends.

Rust prevents the reference from being used afterward.

This is why **ownership and lifetimes are closely related but distinct concepts**:

- **Ownership** determines who is responsible for a value.
- **Lifetimes** constrain how long references to that value may remain valid.

## 9. Ownership enables deterministic resource management

**Ownership is not limited to heap memory.**

The same mechanism can manage operating-system resources such as file descriptors, sockets, and locks.

For example:

```rust
use std::fs::File;

fn main() {
    let file = File::open("data.txt").unwrap();

    // Use file here.
}
```

The `File` value owns an operating-system file handle.

When the owner goes out of scope, the `File` destructor closes the handle.

```text
   File::open()
         |
         v
 Acquire OS Handle
         |
         v
 File owns handle
         |
         v
     Use file
         |
         v
Owner leaves scope
         |
         v
   File::drop()
         |
         v
  Close OS Handle
```

This pattern is known as **RAII (Resource Acquisition Is Initialization)**.

**Resource lifetime is tied to an owning value's lifetime.**

The compiler automatically arranges cleanup along normal scope-exit paths, including stack unwinding when panics use the unwind strategy.

**Destructor execution is not guaranteed in every situation:** process termination, aborting panics, and deliberately leaked values are examples where cleanup may not occur.

## 10. Ownership vs. garbage collection

Ownership and garbage collection solve overlapping problems using different approaches.

| Characteristic          | Rust ownership                             | Tracing garbage collection              |
| ----------------------- | ------------------------------------------ | --------------------------------------- |
| Main tracking mechanism | Compile-time ownership and borrowing rules | Runtime reachability analysis           |
| Resource cleanup        | Usually deterministic                      | Generally nondeterministic              |
| Runtime collector       | Not required                               | Required                                |
| Object sharing          | Borrowing or explicit shared ownership     | References to reachable objects         |
| Memory-safety checks    | Primarily static                           | Primarily runtime-managed memory safety |
| Cyclic references       | Can leak with `Rc`/`Arc` cycles            | Usually collectable if unreachable      |

### Rust's approach

```text
   Compile Time
         |
         v
  Track Ownership
         |
         v
 Verify Borrowing
         |
         v
Generate Drop Logic
         |
         v
      Runtime
         |
         v
   Execute Code
         |
         v
 Release Resources
```

### Tracing garbage collection

```text
       Runtime
          |
          v
  Allocate Objects
          |
          v
 Track Reachability
          |
          v
Identify Unreachable
       Objects
          |
          v
   Reclaim Memory
```

Rust does not need a tracing garbage collector for ordinary owned values.

However, `Drop` still runs at runtime, allocation still has a cost, and reference-counted types such as `Arc<T>` introduce runtime bookkeeping.

**Rust's ownership mechanism is not equivalent to having zero memory-management overhead.**

## 11. Shared ownership: `Rc<T>` and `Arc<T>`

The basic ownership model provides one owner for each value.

Sometimes multiple parts of a program need to participate in owning the same allocation.

Rust supports this explicitly.

### `Rc<T>`: reference-counted ownership

```rust
use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("hello"));

    let b = Rc::clone(&a);
    let c = Rc::clone(&a);

    println!("{}", Rc::strong_count(&a));
}
```

Output:

```text
3
```

Conceptually:

```text
a: Rc             b: Rc             c: Rc
  |                 |                 |
  +-----------------+-----------------+
                    |
                    v
          +------------------+
          | Reference count  |
          |        3         |
          +------------------+
          |      String      |
          |     "hello"      |
          +------------------+
```

**All three `Rc` handles share ownership of one allocation.**

When a handle is dropped, the strong reference count decreases.

**When the strong count reaches zero, the contained value is destroyed.** `Rc<T>` is intended for single-threaded reference counting.

### `Arc<T>`: atomic reference-counted ownership

**`Arc<T>` provides thread-safe reference counting.**

```rust
use std::sync::Arc;

fn main() {
    let value = Arc::new(String::from("hello"));

    let other = Arc::clone(&value);
}
```

Its reference-count operations use atomics.

This makes it suitable for transferring shared ownership across threads, provided the contained type satisfies the required thread-safety bounds.

**An `Arc<T>` does not automatically make arbitrary mutation of `T` thread-safe.** Shared mutation typically requires synchronization such as `Mutex<T>` or atomics.

## 12. Ownership is a compile-time model, not a physical memory location

An important distinction:

**Ownership does not necessarily mean a value lives on the heap.**

```rust
fn main() {
    let a = 42;
    let b = Box::new(100);
}
```

Conceptually:

```text
      Stack                      Heap
+----------------+
| a: i32 = 42    |
+----------------+
| b: Box<i32> ---+--------------> 100
+----------------+
```

Both `a` and `b` are owners.

But they own different kinds of resources:

- `a` owns an inline integer value.
- `b` owns a `Box<i32>`, which owns a heap allocation containing an integer.

The ownership rules apply to both.

Compiler optimizations may alter or eliminate these physical storage locations entirely.

The core abstraction is therefore not _where a value resides_, but **who controls its lifetime and access**.

**Key takeaway:** Rust turns resource ownership into a statically checked contract. Each resource has a responsible owner, moves transfer that responsibility, borrowing grants controlled temporary access, and destructors release resources when ownership ends. This model is the foundation of Rust's memory safety, deterministic cleanup, and efficient systems programming.
