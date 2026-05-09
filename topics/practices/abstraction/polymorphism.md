# Polymorphism

Polymorphism is a core principle of object-oriented programming that allows
objects of different types to be treated as instances of a common superclass
or interface. The word derives from Greek, meaning "many shapes."

In practice, polymorphism allows a single function or method to behave
differently depending on the specific object it is acting upon.

## The core mechanism

Polymorphism is the bridge between abstraction and indirection. By defining a
general "contract" (the abstraction) and using a reference to that contract
(the indirection), the system can decide which specific code to execute at
runtime.

| Feature         | Description                                                     |
|-----------------|-----------------------------------------------------------------|
| Uniformity      | Different classes can be manipulated through the same interface |
| Dynamic binding | Which method to call is determined at runtime, not compile time |
| Extensibility   | New classes can be added without modifying existing code        |

## Types of polymorphism

### Ad-hoc polymorphism (function overloading)

Multiple functions have the same name but different parameters. The compiler
determines which version to call based on arguments.

Example: `print(int i)` and `print(string s)`.

### Parametric polymorphism (generics)

A function or data type is written generically to handle values identically
without depending on their type.

Example: `List<T>` in Java or C# can hold integers, strings, or custom objects
using the same logic.

### Subtype polymorphism (inclusion polymorphism)

The most common form in OOP. A program defines a base class (or interface) and
multiple subclasses provide their own implementations of the base's methods.

## Benefits

- **Eliminates conditional dispatch:** Instead of branching on type
  (`if (type == "Circle") ... else if (type == "Square") ...`), call
  `shape.draw()` and let the object decide how to handle it.
- **Decouples callers from implementations:** High-level logic depends on an
  interface rather than a concrete class, making components independently
  testable and replaceable.
- **Open for extension:** New implementations can be added without modifying
  existing code — a `Triangle` that implements `Shape` works everywhere
  `Shape` is accepted.

## The performance trade-off

In languages like C++ or Java, subtype polymorphism typically uses a **virtual
method table (vtable)**. When a polymorphic method is called:

1. The program looks up the object's vtable
2. It finds the address for the specific method implementation
3. It jumps to that address to execute the code

This "indirect jump" is slightly slower than a direct function call and can
occasionally hinder CPU optimizations like inlining. However, for most
applications, the gain in clarity and maintainability far outweighs this
minor cost.

---

Return to [Abstraction](_index.md)
