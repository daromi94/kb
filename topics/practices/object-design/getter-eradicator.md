# Getter eradicator

The getter eradicator is a design exercise that treats every getter as a
potential design flaw. By attempting to eliminate them, developers are forced
to move behavior closer to data, shifting from procedural style to
object-oriented design. It is most effective as a diagnostic tool rather than
a strict rule.

## The exercise

Challenge each getter: can the caller instead *tell* the object what it needs
to be done? If two or more getters are called on the same object in sequence,
that is a strong signal that a method is missing.

```java
// Two getters signal a missing method
String full = user.getFirstName() + " " + user.getLastName();

// The object should own this logic
String full = user.getFullName();
```

The guiding heuristic is the **information expert** principle: logic belongs
on the object that holds the data it needs. When getters leak data outward,
logic follows, and the object becomes anemic.

## When getters are appropriate

Applying the eradicator dogmatically causes more harm than good. Getters are
legitimate in several contexts:

**Boundary objects:** DTOs, API responses, and database rows exist to carry
data across boundaries. Serialization libraries, UI data binding, and ORMs
often require accessors to function.

**Fundamental properties:** Encapsulation means hiding *design decisions*
(how data is represented), not the data itself. A `Person.getName()` getter
exposing a conceptual property does not break encapsulation. The problem
arises when a getter exposes an implementation detail — returning an
`ArrayList` instead of a `List`, or a raw internal structure that may change.

**Collaboration between objects:** Objects must share information to
collaborate. Forbidding all getters forces workarounds like visitors or
callbacks that add complexity without improving the design.

## The god object trap

Moving all logic into a single class to avoid getters can violate the single
responsibility principle. If an object's data is used in fifty business
contexts, absorbing all fifty into that class creates a god object. The
eradicator should move logic to the *right* object, not pile everything into
the object that holds the data.

---

Return to [Object design](_index.md)
