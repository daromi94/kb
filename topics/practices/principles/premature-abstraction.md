# Premature abstraction

Premature abstraction occurs when a developer generalizes code before having
enough concrete examples to know what the right abstraction looks like. The
motivation is usually noble — DRY code, future-proofing — but the result is
a layer of indirection that doesn't actually simplify anything.

When an abstraction is built from a single use case, it reflects that one
case's shape rather than any true underlying pattern. The codebase is left
with a leaky abstraction that forces every reader to peek under the hood to
understand what is actually happening.

## Costs

| Cost                | Effect                                                                                      |
|---------------------|---------------------------------------------------------------------------------------------|
| Cognitive load      | Simple tasks become hard to understand when buried under generic interfaces and helpers     |
| Indirection fatigue | Developers jump through multiple files and classes to find the actual business logic        |
| Erosion of trust    | Changing a "generic" layer to fix one bug risks breaking unrelated features                 |
| Logic bloat         | Generic handlers accumulate `if/else` ladders and `switch` statements for speculative cases |

## Speculative generality

The antipattern known as "speculative generality" (or "architecture
astronautics") happens when developers look at a single use case and
immediately build a generic framework to handle it. Every line of generic code
must be maintained, documented, and debugged — even if the anticipated
variations never materialize.

The YAGNI principle (You Ain't Gonna Need It) is a direct counter: don't
solve problems you don't have yet.

## Why the wrong abstraction is worse than duplication

It is significantly easier to refactor two specific implementations into one
abstraction than it is to fix one wrong, deeply embedded abstraction. A wrong
abstraction accumulates special cases over time, becoming increasingly costly
to change because every consumer depends on its current shape. Duplication,
by contrast, is localized and easy to delete.

## Related

- [Abstraction](abstraction.md) - What abstraction is and when it helps
- [Rule of three](rule-of-three.md) - Heuristic for when to generalize
- [Indirection](indirection.md) - The flexibility layer that premature abstraction misuses

---

Return to [Principles](_index.md)
