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
live here.

Detail hiding works through **specification** — define what something
does without committing to how. A sorted collection guarantees ordering
and lookup semantics; whether it is a red-black tree, a skip list, or
a B-tree is beneath the line. Design by Contract formalizes this —
preconditions, postconditions, and invariants are the specification,
and any conforming implementation is substitutable.

## Properties

- **Leak-resistant.** Users predict behavior without looking
  underneath; leaks should be rare and predictable
- **Cohesive.** Everything grouped under the concept genuinely belongs
  together; otherwise there is no concept, just a name
- **Consistent level.** The abstraction lives at one level of detail;
  mixing levels breaks it
- **Economically justified.** The cost of learning and maintaining the
  abstraction is repaid by reuse, clarity, or flexibility; otherwise
  it's overhead

## Failure modes

- **Premature.** Built before knowing what varies; leads to flexibility
  where it's not needed and rigidity where it is
- **Under-abstraction.** Too little hidden; raw mechanics show through
  and modules couple
- **Wrong axis.** Generalizes a dimension that doesn't actually vary;
  the abstraction holds only one real case
- **Rename wrapper.** A layer that hides nothing; pure overhead

---

Return to [Abstraction](_index.md)
