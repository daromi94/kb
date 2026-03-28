# Barricades

An architectural boundary that separates untrusted external data
from a trusted interior. All data crossing the barricade gets
validated, sanitized, and transformed into typed internal
representations. Code inside never sees raw external data. The
barricade is the only place where the messy work of handling
untrusted input happens.

This solves the scattering problem. Without a barricade, defensive
checks spread throughout the codebase — inconsistent, redundant in
some places, missing in others, impossible to audit. A barricade
concentrates validation into one layer so everything below it can
assume clean data. That assumption is a structural guarantee, not
wishful thinking.

## The validation pipeline

A barricade processes incoming data in a specific order.

| Step           | Question                                     |
|----------------|----------------------------------------------|
| Presence       | Is the data there at all?                    |
| Structure      | Right shape, right types, expected fields?   |
| Semantics      | Valid in the domain? Consistent references?  |
| Sanitization   | Safe? No injection, traversal, control chars |
| Normalization  | Consistent format? Trimmed, encoded, cased?  |
| Transformation | Converted to a typed internal object?        |

The final step is the most important. Raw strings and untyped
dictionaries become strongly-typed domain objects — a JSON blob
becomes a ValidatedOrder, a query string becomes a SearchQuery.
The type itself is proof of validity: if the object exists, the
data passed every check.

## Where barricades go

A barricade sits at every point where data crosses a trust boundary.

**External input.** HTTP handlers, CLI parsers, file readers,
message queue consumers. The most critical barricade. Data here has
zero guarantees.

**Third-party integrations.** Responses from external APIs and
partner systems. Often under-barricaded because developers trust
the documentation. Fields go missing, types change, nulls appear
where the docs say they will not.

**Database reads.** Data the system wrote is not automatically
trustworthy. Other systems, manual queries, flawed migrations, and
bugs in previous versions all corrupt stored data. A read-side
barricade catches values that were valid when written but no longer
match current expectations.

**Configuration loading.** Validate at startup: types, ranges,
required fields, mutual consistency. A config failure at boot is
far preferable to discovering an invalid value at 3am.

**Inter-module boundaries.** Controversial for single-team
codebases where assertions and types suffice. Compelling in large
codebases or microservice architectures where trust between teams
is lower and services may run different versions with divergent
assumptions.

## Layered barricades

Real systems have nested barricades at different granularities,
each handling concerns appropriate to its level.

```
+---------------------------------------------------+
| Outer barricade                                   |
| Structural validation, type conversion            |
+---------------------------------------------------+
                       |
                       v
+---------------------------------------------------+
| Service barricade                                 |
| Business rule validation (inventory, permissions) |
+---------------------------------------------------+
                       |
                       v
+---------------------------------------------------+
| Core domain logic                                 |
| Pure computation, no validation                   |
+---------------------------------------------------+
                       |
                       v
+---------------------------------------------------+
| Persistence barricade                             |
| Schema conformance, referential integrity         |
+---------------------------------------------------+
```

The outer barricade does not know about business rules. The service
barricade does not parse raw strings. Responsibilities separate
cleanly across layers.

## The interior payoff

Interior code sheds all validation armor. Without a barricade, a
function three layers deep is half validation checks making policy
decisions that belong at the boundary. With a barricade, the same
function is pure business logic — shorter, easier to read, test,
and verify.

Assertions still have a role in the interior. They guard
against internal bugs (a calculation returning a negative total)
rather than external bad data. The model: validation at the
boundary, assertions for invariants in the interior, clean logic
in between.

## Error translation

Barricades are the natural location for error translation. Inside,
errors use domain terms — InsufficientInventory, CustomerNotFound.
Outside, errors use interface terms — HTTP 400 with a JSON body,
a CLI message with a nonzero exit code. The barricade translates
between the two, keeping domain logic free of transport concerns
and external interfaces free of internal details.

## Barricade bypass

The specific failure mode: a code path that lets external data
reach the interior without passing through the barricade. Common
causes: a new endpoint that skips validation middleware, a
background job that reads from a queue without checking, a
convenience method that accepts raw strings instead of typed
objects.

Bypass is insidious because the system appears protected — the
barricade exists and validates thoroughly, but there is a hole in
the wall. Architectural enforcement is more reliable than developer
discipline. The strongest pattern in typed languages: make internal
types unconstructable outside the barricade. If ValidatedOrder can
only be created by a factory method inside the validation module,
bypass requires a conscious, visible act that shows up in code
review.

## Related

- [Defensive programming](defensive-programming.md) - The broader
  principle barricades implement

---

Return to [Principles](_index.md)
