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

| Feature         | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| Uniformity      | Different classes can be manipulated through the same interface          |
| Dynamic binding | Which method to call is determined at runtime, not compile time          |
| Extensibility   | New classes can be added without modifying existing code                 |

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

## The universal remote analogy

A universal remote has a "Power" button designed to work with any television.

- **The abstraction:** The "Power" button is the interface. Every TV must have
  a way to turn on or off.
- **The polymorphism:** When you press "Power," the remote sends a signal. A
  Sony TV interprets it one way, a Samsung another. You don't need to know the
  specific infrared frequency for each brand; you only need to know how to
  press "Power."

## Clean code benefits

Polymorphism reduces the WTF/minute count by eliminating complex conditional
logic.

- **Replacing if/else or switch blocks:** Instead of a giant switch checking
  object type (`if (type == "Circle") drawCircle(); else if (type == "Square")...`),
  simply call `shape.draw()`. The object knows how to draw itself.
- **Dependency inversion:** High-level logic depends on an interface rather
  than a concrete implementation. This makes code easier to test (via mocking)
  and easier to modify.
- **Plug-and-play architecture:** Add a `Triangle` class to the system, and as
  long as it implements `Shape`, the rest of the application works with it
  immediately without changing a single line of original logic.

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

## Related

- [Abstraction](abstraction.md) - Polymorphism builds on abstraction
- [Indirection](indirection.md) - Dynamic dispatch is a form of indirection
- [Law of Demeter](law-of-demeter.md) - Polymorphism helps comply with LoD
