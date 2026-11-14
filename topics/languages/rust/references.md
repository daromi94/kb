# References

A **reference** is a way to access a value without taking ownership of it.

References are central to Rust's ownership model because they allow values to be shared or modified without transferring ownership or copying the underlying data.

Rust has two primary kinds of references:

- **Shared references (`&T`)** allow reading a value without taking ownership.
- **Mutable references (`&mut T`)** allow reading and modifying a value through exclusive access.

The act of creating a reference is called **borrowing**.

## 1. The problem references solve

Consider a function that calculates the length of a string.

```rust
fn calculate_length(s: String) -> usize {
    s.len()
}

fn main() {
    let text = String::from("hello");

    let length = calculate_length(text);

    println!("{text}");
}
```

This program does not compile.

The function receives a `String` by value, so ownership moves into the function.

```text
   main()                        calculate_length()
      |                                   |
      |                                   |
text: String                              |
      |                                   |
      +--------- move ownership --------->|
                                          |
                                      s: String
                                          |
                                          v
                                        len()
                                          |
                                          v
                                       dropped
```

After the function call, `text` can no longer be used.

A possible solution is to clone the string, but cloning allocates and copies the heap contents.

Instead, Rust provides references.

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}

fn main() {
    let text = String::from("hello");

    let length = calculate_length(&text);

    println!("{text}: {length}");
}
```

Here:

- **`&text`** creates a reference to `text`.
- **`s: &String`** declares that the function accepts a reference.
- **Ownership remains with `text`.**
- The function can access the string without owning it.

```text
     main()
        |
        v
+----------------+                      +----------------+
| text: String   |<------ borrows ------| s: &String     |
+----------------+                      +----------------+
        |                                       |
        | owns                                  v
        v                              calculate_length()
  Heap: "hello"
```

When `calculate_length` returns, the reference is no longer needed. The original `String` remains valid.

**Borrowing separates access to a value from ownership of that value.**

## 2. Shared references: `&T`

**A shared reference allows access to a value without granting permission to mutate it through that reference.**

```rust
fn print_length(value: &String) {
    println!("{}", value.len());
}
```

**Multiple shared references can exist simultaneously.**

```rust
fn main() {
    let text = String::from("hello");

    let r1 = &text;
    let r2 = &text;
    let r3 = &text;

    println!("{r1} {r2} {r3}");
}
```

Conceptually:

```text
             Stack
       +----------------+     owns
       | text: String   |-----------------> Heap Data
       +----------------+                   "hello"
               ^
               |
   +-----------+-----------+
   |           |           |
   |           |           |
  r1          r2          r3
&String     &String     &String
```

All three references point to the same underlying string.

The string is not cloned.

**The references do not independently own the heap allocation.**

### Why prohibit mutation through shared references?

Suppose one reference could modify the string while another reference was reading it.

The reader might observe an unexpected state, or a mutation could trigger reallocation and invalidate assumptions about the data.

Rust prevents such conflicting access through its borrowing rules.

For ordinary types, a shared reference permits reading but not mutation:

```rust
fn modify(value: &String) {
    value.push_str(" world");
}
```

This fails to compile because `push_str` requires mutable access.

There are exceptions through **interior mutability**, such as `Cell`, `RefCell`, and `Mutex`, which provide controlled mutation behind shared references.

## 3. Mutable references: `&mut T`

**A mutable reference provides temporary exclusive access to a value.**

```rust
fn append_world(value: &mut String) {
    value.push_str(" world");
}

fn main() {
    let mut text = String::from("hello");

    append_world(&mut text);

    println!("{text}");
}
```

Output:

```text
hello world
```

The important difference is that the function receives permission to modify the original value.

```text
      main()
         |
         v
   text: String
         |
         | exclusive borrow
         v
value: &mut String
         |
         v
push_str(" world")
         |
         v
text: "hello world"
```

No new `String` is created.

The function modifies the original string directly.

### Mutable references are exclusive

Consider:

```rust
fn main() {
    let mut text = String::from("hello");

    let r1 = &mut text;
    let r2 = &mut text;

    println!("{r1} {r2}");
}
```

This does not compile.

Both mutable references would need to be active simultaneously.

```text
                 String
                    |
        +-----------+-----------+
        |                       |
        v                       v
 r1: &mut String         r2: &mut String
        |                       |
        +-----------X-----------+
                    |
               Conflicting
             mutable access
```

**Rust rejects overlapping exclusive borrows of the same value.**

This is the foundation of one of Rust's most important guarantees:

**At a given point, a value can have multiple active shared borrows or an active exclusive mutable borrow, but not both.**

The rule is more precisely about overlapping access to the same memory. Rust can permit simultaneous mutable references to provably disjoint parts of a structure.

## 4. Shared and mutable references cannot conflict

Consider:

```rust
fn main() {
    let mut text = String::from("hello");

    let reader = &text;
    let writer = &mut text;

    println!("{reader}");
    writer.push_str(" world");
}
```

This fails because `reader` remains live when the mutable borrow is created.

```text
             text
               |
   +-----------+-----------+
   |                       |
   v                       v
reader                  writer
&String               &mut String
   |                       |
   +-----------X-----------+
               |
        Borrow conflict
```

**The compiler prevents a mutable reference from overlapping with an active shared reference.**

However, Rust uses **non-lexical lifetimes (NLL)** to determine when references are actually needed.

This is valid:

```rust
fn main() {
    let mut text = String::from("hello");

    let reader = &text;

    println!("{reader}");

    let writer = &mut text;

    writer.push_str(" world");
}
```

Why?

The final use of `reader` occurs before `writer` is created.

```text
     Execution
         |
         v
   Create reader
         |
         v
    Read String
         |
         v
Last use of reader
         |
         v
Shared borrow ends
         |
         v
   Create writer
         |
         v
   Modify String
```

Although the `reader` binding remains lexically in scope, the borrow need not remain active until the closing brace.

**This is a critical distinction:** **the lifetime of a borrow is not always identical to the lexical scope of the reference variable.**

## 5. References and memory

At the machine level, a reference is usually represented using an address.

Consider:

```rust
let x = 42;
let r = &x;
```

Conceptually:

```text
         Memory

  Address       Value
+----------+------------+
| 0x1000   | x = 42     |
+----------+------------+
| 0x2000   | r = 0x1000 |
+----------+------------+
```

The reference `r` refers to the location containing `x`.

This resembles a pointer in C or C++.

However, Rust references carry additional **compile-time validity and aliasing requirements**.

**A safe Rust reference must refer to a valid, properly aligned value of its type and must not outlive that value.** Rust's borrowing rules also constrain how references can alias memory.

The compiler can therefore reject many invalid memory-access patterns before execution.

The address diagram is conceptual: the compiler may keep variables in registers, eliminate them, or choose different physical representations.

### References are not necessarily one machine word

A reference to a sized type is typically pointer-sized:

```rust
&i32
&String
&Vec<u8>
```

**But references to dynamically sized types can carry additional metadata.**

For example, `&str` and `&[u8]` are commonly represented as two machine words:

```text
     &str
+-------------+
| Pointer     |------> String bytes
+-------------+
| Length      |
+-------------+
```

This is why `&str` can represent a view of some string data without owning or copying it.

## 6. References and lifetimes

**A reference is only valid while the referenced value remains alive.**

Consider:

```rust
fn invalid_reference() -> &String {
    let text = String::from("hello");

    &text
}
```

This does not compile.

The function attempts to return a reference to a local value that will be destroyed when the function returns.

```text
   Function Scope
          |
          v
    text: String
          |
          v
    return &text
          |
          v
   Function exits
          |
          v
   text is dropped
          |
          v
   Reference would
point to invalid data
```

Rust rejects this because the reference cannot remain valid after `text` is destroyed.

A correct approach is to return ownership:

```rust
fn create_string() -> String {
    String::from("hello")
}
```

Or borrow a value owned by the caller:

```rust
fn identity(value: &String) -> &String {
    value
}
```

In the second example, the returned reference is valid only as long as the borrowed value remains valid.

Rust uses lifetimes to express and verify these relationships.

## 7. References vs. ownership vs. cloning

These three operations serve fundamentally different purposes.

Consider:

```rust
let a = String::from("hello");
```

### Move ownership

```rust
let b = a;
```

```text
     Before                       After

a --------> Data            b --------> Data

                            a: invalid
```

**The heap contents are not cloned. Ownership transfers to `b`.**

### Borrow

```rust
let b = &a;
```

```text
b: &String
    |
    v
    a --------> Data
```

**Both bindings can be used, but only `a` owns the string.**

### Clone

```rust
let b = a.clone();
```

```text
a --------> Data A

b --------> Data B
```

**Two independently owned strings exist, each with its own heap allocation.**

| Operation           | New owner?       | Copies string bytes? | Original usable? |
| ------------------- | ---------------- | -------------------- | ---------------- |
| `let b = a`         | Yes, transferred | No                   | No               |
| `let b = &a`        | No               | No                   | Yes              |
| `let b = a.clone()` | Yes, independent | Yes                  | Yes              |

This distinction is one of the most important parts of Rust's performance model.

## 8. Prefer `&str` over `&String` for read-only string parameters

Consider:

```rust
fn greet(name: &String) {
    println!("Hello, {name}");
}
```

This works, but a more flexible signature is:

```rust
fn greet(name: &str) {
    println!("Hello, {name}");
}
```

Why?

Because `&str` represents a borrowed view of UTF-8 string data.

It can accept string literals and borrowed string data from `String` values.

```rust
fn main() {
    let owned = String::from("Rust");

    greet(&owned);
    greet("World");
}
```

**`&str` is often the more general interface when only string contents are needed.**

The same design principle applies to collections.

Prefer:

```rust
fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}
```

Over:

```rust
fn sum(values: &Vec<i32>) -> i32 {
    values.iter().sum()
}
```

The slice-based version accepts arrays, vectors, and other contiguous sequences through appropriate borrowing conversions.

**Engineering principle: APIs should generally borrow the least restrictive abstraction that provides the required functionality.**

## 9. References are not garbage-collected pointers

**Rust references do not require a garbage collector to determine when memory can be reclaimed.**

```text
   Ownership System
           |
           v
 Compiler tracks moves
     and borrowing
           |
           v
Borrow checker ensures
 valid reference usage
           |
           v
Owner eventually drops
       the value
```

**A reference does not ordinarily keep its target alive through runtime reference counting.**

Instead, the borrow checker ensures that safe references cannot be used after their referents are invalidated.

For shared ownership that can outlive individual scopes, Rust provides types such as `Rc<T>` and `Arc<T>`, which use reference counting. These are separate mechanisms from ordinary borrowing.

**Key takeaway:** Ownership determines who is responsible for a value. References determine who may access it, how they may access it, and for how long. Rust enforces those relationships at compile time, enabling memory safety without requiring garbage collection.
