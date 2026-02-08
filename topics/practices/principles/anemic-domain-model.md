# Anemic domain model

The anemic domain model is an anti-pattern where domain objects contain state
(data) but lack behavior (logic). Objects are named after business nouns
(`Order`, `Customer`) with rich relationships, yet they are little more than
bags of getters and setters. The actual business logic lives in separate
Service or Manager classes, making the design procedural despite using an
object-oriented language.

## Example

Anemic — the entity is a data bag, logic lives elsewhere:

```java
class Order {
    private List<LineItem> items;
    private String status;
    // getters and setters for everything
}

class OrderService {
    void confirm(Order order) {
        if (order.getItems().isEmpty())
            throw new IllegalStateException("no items");
        if (!order.getStatus().equals("DRAFT"))
            throw new IllegalStateException("already confirmed");
        order.setStatus("CONFIRMED");
    }
}
```

Rich — the entity owns its rules and protects its invariants:

```java
class Order {
    private List<LineItem> items;
    private Status status = Status.DRAFT;

    void confirm() {
        if (items.isEmpty())
            throw new IllegalStateException("no items");
        if (status != Status.DRAFT)
            throw new IllegalStateException("already confirmed");
        status = Status.CONFIRMED;
    }
}
```

In the anemic version, any service can call `setStatus("CONFIRMED")` and skip
validation entirely. The entity cannot defend itself. In the rich version,
there is no setter — the only path to confirmation runs through the business
rules.

## Symptoms

**Logic displacement:** Validations, calculations, and business rules live in
service classes (`OrderService`) rather than on the entities they govern.

**Logic duplication:** Because logic is not anchored to its data, it scatters
across multiple services. Two services that both confirm orders may enforce
subtly different rules.

**Poor discoverability:** A developer looking at a `Product` class cannot see
what operations are possible; they must search through service classes to find
the relevant logic.

## Anemic vs rich domain model

| Feature     | Anemic                              | Rich                                  |
|-------------|-------------------------------------|---------------------------------------|
| Logic       | In separate Service/Manager classes | Inside the domain entities            |
| Data access | Public getters and setters          | Private setters; methods change state |
| Consistency | External services enforce (fragile) | Entity enforces its own invariants    |
| Style       | Procedural (transaction scripts)    | Object-oriented                       |
| Best fit    | Simple CRUD applications            | Complex business domains              |

## Why it happens

**Data-centric thinking:** Developers accustomed to relational databases view
objects as rows in memory rather than encapsulated behavior.

**Framework influence:** Many frameworks encourage a layered architecture that
naturally separates data objects from service logic, nudging developers toward
anemia by default.

**Tooling bias:** IDE generators and libraries that auto-create getters and
setters make it effortless to build hollow objects, steering designs away from
rich behavior.

## Related

- [Tell, don't ask](tell-dont-ask.md) - The principle that directly counters anemia
- [Abstraction](abstraction.md) - Rich models use abstraction to hide state

---

Return to [Principles](_index.md)
