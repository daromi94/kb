# Abstraction

Hiding details that don't matter at a given level of reasoning, exposing
only what is essential to use or think about something. Less a technique
than a discipline: choosing which facts to promote into a concept and
which to suppress as implementation noise.

Abstraction manages how much of a system a human must hold in their head
at once. Reuse, substitutability, and testability are downstream benefits.
When an abstraction stops shrinking the mental model, it has stopped
earning its keep.

## Two directions

- **Generalization:** Extract commonalities into a single representation
  that covers all cases
- **Detail hiding:** Expose the "what," conceal the "how"

Generalization works through **parameterization** — replace fixed
details with parameters so one construct serves many cases. Generics,
higher-order functions, strategy objects, and dependency injection all
live here. Instead of twenty sort routines, write one parameterized by
a comparator.

Detail hiding works through **specification** — define what something
does without committing to how. A sorted collection guarantees ordering
and lookup semantics; whether it is a red-black tree, a skip list, or
a B-tree is beneath the line. Design by Contract formalizes this —
preconditions, postconditions, and invariants are the specification,
and any conforming implementation is substitutable.

## Properties

- **Leak-resistant.** The user rarely needs to look underneath to predict
  behavior. Spolsky's law of leaky abstractions reminds us this is an
  ideal, not a guarantee
- **Cohesive.** The things grouped under the concept genuinely belong
  together, not a bag of unrelated operations sharing a name
- **Consistent level.** Mixing "open a TCP socket" and "send a password
  reset email" in the same module is a level violation
- **Economically justified.** Every abstraction bets that the cost of
  learning and maintaining the concept will be repaid by reuse, clarity,
  or flexibility

## Failure modes

- **Premature.** Invents concepts for imagined futures and ossifies the
  wrong seams
- **Under-abstraction.** Drowns readers in incidental detail and couples
  modules that should be independent
- **Wrong axis.** Generalizes along a dimension the domain doesn't vary
  on — the symptom is a base class with one real subclass and a second
  "example" nobody uses
- **Rename wrapper.** Forwards every call to the thing it wraps, adding
  a layer without hiding anything

## Related

- [Leaky abstractions](leaky-abstractions.md) - When hidden complexity surfaces
- [Premature abstraction](premature-abstraction.md) - Costs of abstracting too early
- [Design by Contract](design-by-contract.md) - Formalizes abstraction by specification
- [Indirection](indirection.md) - Closely related but serves different purpose
- [Polymorphism](polymorphism.md) - Uses abstraction for dynamic behavior

---

Return to [Principles](_index.md)
