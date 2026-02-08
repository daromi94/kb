# Information expert

Information expert is a GRASP pattern for assigning responsibilities in
object-oriented design. The rule: assign a responsibility to the class that
has the information necessary to fulfill it. "Information" means data stored
in fields, knowledge of related objects, or the ability to derive a value.

## Identifying the expert

Ask: *who has the data this logic needs?* When multiple objects each hold
part of the answer, each one computes its piece and the containing object
aggregates.

### Example: sale total

A `Sale` contains `SalesLineItem` objects. Each line item knows its quantity
and product price; the sale knows its line items.

```java
class SalesLineItem {
    private int quantity;
    private Money unitPrice;

    Money subtotal() {
        return unitPrice.times(quantity);
    }
}

class Sale {
    private List<SalesLineItem> items;

    Money total() {
        return items.stream().map(SalesLineItem::subtotal).reduce(Money.ZERO, Money::add);
    }
}
```

No `PricingService` reaches into these objects. Each class computes what it
can from its own data, and the sale assembles the result.

## Benefits

**Encapsulation:** Data stays private. External code calls a high-level method
rather than extracting fields.

**Low coupling:** Callers depend on behavior, not internal structure. Changing
how a subtotal is calculated (adding tax, discounts) affects only the expert.

**High cohesion:** Each class stays focused on behaviors related to its own
data.

## When to override the expert

The expert is the default choice, but three situations justify placing logic
elsewhere:

**God object risk:** A data-rich class that absorbs every responsibility
touching its fields becomes bloated. Split responsibilities across
collaborators when cohesion drops.

**Infrastructure concerns:** A `User` object holds enough information to
persist itself, but database access belongs in a repository, not a domain
object. Layered architecture takes precedence over the expert for
infrastructure responsibilities.

**Cross-cutting concerns:** Logging, security, and auditing touch many
objects. Duplicating that logic in every expert class creates massive
repetition; these belong in interceptors or middleware.

## Related

- [Tell, don't ask](tell-dont-ask.md) - Enforces the expert by commanding objects
- [Getter eradicator](getter-eradicator.md) - Diagnostic tool guided by the expert
- [Anemic domain model](anemic-domain-model.md) - What happens when the expert is ignored

---

Return to [Principles](_index.md)
