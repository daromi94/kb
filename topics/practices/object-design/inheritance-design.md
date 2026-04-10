# Inheritance design

Design and document for inheritance or prohibit it. A class is either a
documented foundation built for extension or a sealed leaf. Leaving a class
open without deliberate design creates the fragile base class problem.

From Joshua Bloch, *Effective Java*.

## The fragile base class

Inheritance is the strongest form of coupling. Two risks arise when a class
is extended without explicit design:

**Internal self-use:** If superclass method `A` calls its own method `B`, a
subclass overriding `B` breaks `A` without warning. The subclass author has
no way to know that `B` is called internally.

**Evolution risk:** Adding a method to the superclass that collides with a
subclass method causes compilation errors or silent behavioral changes.

## Designing for extension

When inheritance is intentional, the class must be treated as a framework
for subclasses, not a black box:

**Hook methods:** Provide `protected` methods that subclasses override to
plug in behavior without disrupting the superclass flow.

**Final by default:** Any method not intended for overriding should be
`final`. The designer decides exactly which extension points exist.

**Constructor safety:** Constructors must never invoke overridable methods.
The subclass state is uninitialized when the superclass constructor runs,
so an overridden method would operate on incomplete data.

## Documenting for extension

Documentation for overridable methods must expose implementation details —
one of the few places this is appropriate:

- Which other methods in the class call this method (self-use patterns)
- What happens to the rest of the class if this method is overridden
- Threading and synchronization requirements for subclass implementations

## Prohibiting inheritance

When a class is not designed for extension, seal it:

**Final classes:** Marking the class `final` prevents all subclassing.

**Private constructors:** Making constructors private and exposing static
factory methods prevents external extension while allowing controlled
internal subclasses.

## Composition over inheritance

The preferred alternative to implementation inheritance. Instead of
extending a class, hold an instance of it as a private field:

| Aspect      | Inheritance                          | Composition                        |
|-------------|--------------------------------------|------------------------------------|
| Coupling    | Subclass depends on internal details | Client depends on public interface |
| Flexibility | Fixed at compile time                | Swappable at runtime               |
| Safety      | Fragile base class risk              | No self-use or evolution hazards   |
| Reuse       | Tied to one superclass               | Can compose from multiple objects  |

Composition treats the other class as a black box, depending only on its
public interface. It avoids the self-use and fragile base class problems
entirely.

---

Return to [Object design](_index.md)
