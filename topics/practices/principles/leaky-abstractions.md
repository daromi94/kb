# Leaky abstractions

All non-trivial abstractions leak some of their underlying complexity.
Joel Spolsky coined this as the Law of Leaky Abstractions: the
simplification an abstraction provides is never total, and the details
it hides will surface in unexpected ways.

## How abstractions leak

A network call wrapped to look like a local function call still fails in
fundamentally different ways — timeouts, partial failures, ordering
issues. An ORM that hides SQL still produces slow queries when the
abstraction doesn't map cleanly to the underlying joins. A "portable"
GUI toolkit still looks slightly wrong on every platform.

The leak happens when the consumer must understand the layer below to
debug, tune, or work around the abstraction's limitations. At that
point, the abstraction hasn't eliminated complexity — it has added a
layer on top of it.

## Living with leaks

The goal is not to build leak-proof abstractions — that's impossible.
The goal is to choose abstractions where the leaks are manageable and
the simplification is worth the cost. A good abstraction leaks rarely
and in predictable places. A bad one leaks constantly, forcing the
consumer to hold two mental models at once: the abstraction and the
reality behind it.

## Related

- [Abstraction](abstraction.md) - Core concept and benefits
- [Indirection](indirection.md) - Each layer of indirection is a potential leak point

---

Return to [Principles](_index.md)
