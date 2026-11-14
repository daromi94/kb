# Prelude

The **prelude** is a collection of commonly used types, traits, and other items that Rust automatically imports into every module.

Its purpose is to make frequently used language features available without requiring explicit `use` declarations.

## 1. The problem the prelude solves

Consider this Rust program:

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    let text = String::from("hello");

    let result: Option<i32> = Some(42);

    println!("{text}");
}
```

Notice that `String`, `Option`, `Some`, and `vec!` are available without imports.

Normally, items from other modules must be imported explicitly:

```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::new();
    map.insert("key", 42);
}
```

Why does `String` work without `use`, but `HashMap` requires one?

Because **`String` belongs to Rust's standard prelude, while `HashMap` does not.**

Conceptually, the compiler makes prelude items available in every module:

```text
                  Rust Program
                        |
                        v
                +---------------+
                |    Module     |
                +---------------+
                        |
        +---------------+---------------+
        |                               |
        v                               v
Explicit Imports                Implicit Prelude
        |                               |
        v                               v
     HashMap                         String
                                     Option
                                     Result
                                     Vec
                                     Some
                                     None
                                     Ok
                                     Err
                                     ...
```

**The prelude is not a special runtime component. It is part of Rust's name-resolution system.**

## 2. What does the prelude contain?

The standard prelude includes several categories of commonly used items.

| Category            | Examples                                   |
| ------------------- | ------------------------------------------ |
| Types               | `String`, `Vec`, `Box`, `Option`, `Result` |
| Enum variants       | `Some`, `None`, `Ok`, `Err`                |
| Traits              | `Clone`, `Copy`, `Default`, `Iterator`     |
| Conversion traits   | `From`, `Into`, `AsRef`, `AsMut`           |
| Collection traits   | `IntoIterator`, `FromIterator`, `Extend`   |
| Ownership helpers   | `ToOwned`, `ToString`                      |
| Drop-related traits | `Drop`                                     |

**The exact contents depend on the Rust edition.** For example, the 2021 edition added `TryInto`, `TryFrom`, and `FromIterator` to the prelude.

The 2024 edition added `IntoFuture` and `Future` to the prelude.

A common misconception is that every built-in-looking feature comes from the prelude. Primitive types such as `i32`, `bool`, and `str`, and language keywords such as `match` and `fn`, are available through language mechanisms rather than ordinary prelude imports.

## 3. Why traits in the prelude matter

The prelude is particularly important because Rust uses traits to provide methods.

Consider:

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    for number in numbers.iter() {
        println!("{number}");
    }
}
```

The `Iterator` trait is imported automatically.

This means iterator methods are available without explicitly writing:

```rust
use std::iter::Iterator;
```

The method `.map()` is another example:

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    let doubled: Vec<i32> = numbers
        .into_iter()
        .map(|n| n * 2)
        .collect();

    println!("{doubled:?}");
}
```

The prelude makes `Iterator` and `IntoIterator` available for method lookup, while the concrete types and trait implementations determine which operations are supported.

```text
        Vec<i32>
            |
            v
   IntoIterator Trait
            |
            v
       into_iter()
            |
            v
        Iterator
            |
      +-----+-----+
      |           |
      v           v
    map()     collect()
```

**An important distinction:** **importing a trait does not make a type implement it.**

A type must still have an appropriate trait implementation for its methods to be usable.

## 4. Can the prelude be disabled?

Yes. The automatically injected standard prelude can be disabled at the crate level using:

```rust
#![no_implicit_prelude]
```

This is an advanced feature, typically useful for compiler tests, name-resolution experiments, or special environments.

After disabling the implicit prelude, ordinary unqualified references to its items are no longer available.

Explicit paths can still be used:

```rust
#![no_implicit_prelude]

extern crate std;

use std::convert::From;

fn main() {
    let text = std::string::String::from("hello");
    std::println!("{}", text);
}
```

**The prelude is a convenience mechanism, not a requirement for using the standard library.**

## 5. Why Rust keeps the prelude small

Rust deliberately avoids importing every standard-library item automatically.

A very large prelude would increase the chance of name collisions and make it harder to determine where types and methods originate.

For example, `HashMap`, `HashSet`, `Arc`, `Mutex`, and `Duration` still normally require explicit imports.

```rust
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::Duration;
```

These declarations document dependencies and keep module namespaces relatively predictable.

A related Rust design principle is that **common, foundational abstractions should be convenient, while specialized abstractions should remain explicit.**

## 6. Key takeaway

```text
                   Rust Module
                        |
        +---------------+---------------+
        |                               |
        v                               v
Explicit Imports                Automatic Prelude
        |                               |
        v                               v
     HashMap                         String
     HashSet                         Vec
     Arc                             Option
     Mutex                           Result
     Duration                        Iterator
                                     Clone
                                     Copy
```

The prelude is fundamentally about **name resolution and ergonomics**, not memory management, runtime performance, or code generation.

It allows Rust programs to use foundational types, traits, and enum variants without repetitive imports while preserving explicit imports for more specialized functionality.
