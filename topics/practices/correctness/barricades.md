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
message queue consumers. Data here has zero guarantees.

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
preferable to discovering an invalid value during runtime.

**Inter-module boundaries.** Controversial for single-team
codebases where assertions and types suffice. Compelling in large
codebases or microservice architectures where trust between teams
is lower and services may run different versions with divergent
assumptions.

## Layered barricades

Real systems have nested barricades at different granularities,
each handling concerns appropriate to its level.

```text
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
decisions that belong at the boundary:

```text
function calculateTotal(order):
    if order is null
        throw error "order is null"
    if order.items is null or order.items is empty
        throw error "order has no items"

    total = 0
    for each item in order.items
        if item is null
            skip to next item
        if item.price is null or item.price < 0
            throw error "invalid price"
        if item.quantity is null or item.quantity < 1
            throw error "invalid quantity"
        total = total + (item.price * item.quantity)

    if order.discount is not null and order.discount >= 0 and order.discount <= 1
        total = total * (1 - order.discount)
    return total
```

With a barricade, the same function is pure business logic:

```text
// ValidatedOrder guarantees: items is non-empty,
// every item has positive price and quantity,
// discount is between 0.0 and 1.0

function calculateTotal(order: ValidatedOrder):
    subtotal = sum of (item.price * item.quantity) for each item in order.items
    result = subtotal * (1 - order.discount)
    assert result >= 0
    return result
```

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
types unconstructable outside the barricade.

```text
type ValidatedOrder =
    productId  : ProductId
    quantity   : Integer
    customerId : CustomerId

    private constructor

    static function validate(raw) -> ValidatedOrder:
        if raw["product_id"] is not a string
            throw ValidationError("product_id is required")

        if raw["quantity"] is not an integer
            throw ValidationError("quantity must be an integer")
        if raw["quantity"] < 1 or raw["quantity"] > MAX_ORDER_QUANTITY
            throw ValidationError("quantity out of range")

        if raw["customer_id"] is not a string
            throw ValidationError("customer_id is required")

        return new ValidatedOrder(
            productId  = ProductId(raw["product_id"]),
            quantity   = raw["quantity"],
            customerId = CustomerId(raw["customer_id"])
        )
```

The only way to get a ValidatedOrder is through `validate()`.
Circumventing this requires reflection or modifying the type
definition — both obvious, reviewable decisions, not silent
oversights.

---

Return to [Correctness](_index.md)
