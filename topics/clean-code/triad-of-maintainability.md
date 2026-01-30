# Triad of maintainability

Source: Codely

Clean code is defined by how little resistance it offers to a developer's mind.
When code is "easy," it minimizes the time between looking at a file and being
able to safely change it. This lifecycle involves three distinct stages.

## 1. Easy to read (the visual layer)

Reading code is the act of scanning text. If code is cluttered, the brain
wastes energy on syntax rather than logic.

- **Meaningful names:** Variables like `daysUntilExpiration` tell a story,
  whereas `d1` requires a search for context
- **Formatting:** Consistent indentation and vertical whitespace act as
  "punctuation," grouping related thoughts together
- **Small units:** A 20-line function can be read in a single glance; a
  200-line function requires scrolling and memory retention

## 2. Easy to understand (the cognitive layer)

Understanding is the act of building a mental model of how the code works.
Clean code makes this model obvious.

- **Single responsibility principle:** Each function or class should do one
  thing. When a function has one job, its behavior is predictable
- **No "magic":** Hardcoded numbers (e.g., `86400`) are replaced by named
  constants (e.g., `SECONDS_IN_A_DAY`), eliminating guesswork
- **Linear logic:** Clean code avoids "spaghetti logic" (excessive jumping
  between files or deep nesting) so the reader can follow execution top to
  bottom

## 3. Easy to modify (the structural layer)

Modification is the ultimate test of clean code. If a codebase is "fragile,"
a change in one place breaks an unrelated feature.

| Characteristic  | Why it simplifies modification                                              |
| --------------- | --------------------------------------------------------------------------- |
| Decoupling      | Changing database logic won't break the UI because they aren't wired together |
| Testability     | High-quality code is easy to wrap in automated tests, providing safety nets |
| Extensibility   | New features can be added by writing new code rather than hacking old code  |

## The economic argument

While writing clean code may take more time initially, it dramatically reduces
the **total cost of ownership**.

- **Messy code:** Development speed starts fast but hits a "technical debt
  wall" where every new feature takes weeks because of the complexity
- **Clean code:** Development speed remains constant. Because the code is easy
  to read, understand, and modify, the team can pivot or scale without the
  system collapsing under its own weight

## Related

- [[wtfs-per-minute]] - How to measure these qualities
- [[abstraction]] - Key technique for all three layers
