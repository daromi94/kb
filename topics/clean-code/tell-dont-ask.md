# Tell, don't ask

Source: Codely

"Tell, don't ask" (TDA) is a design principle that encourages developers to
command objects to perform tasks rather than querying their internal state to
make decisions on their behalf. It is the practical application of
**encapsulation**, ensuring that data and the logic that operates on that data
remain in the same place.

When this principle is ignored, code becomes procedural and "anemic," where
objects are merely bags of data (getters/setters) and the actual "thinking"
happens elsewhere.

## The procedural approach: asking

In an "ask-style" architecture, the caller retrieves information from an
object, processes it, and then tells the object what its new state should be.
This creates high coupling because the caller must understand the internal
rules of the object it is manipulating.

**The workflow of "asking":**

1. Request: Ask the object for its current state
2. Evaluate: Apply business logic to that state outside of the object
3. Update: Set the new state back into the object

| Characteristic   | Ask (procedural)                           | Tell (object-oriented)               |
| ---------------- | ------------------------------------------ | ------------------------------------ |
| Logic location   | Spread across multiple callers             | Centralized within the object        |
| Coupling         | High; callers depend on internal structures | Low; callers depend on stable behaviors |
| Maintenance      | Changing a rule requires updating every caller | Changing a rule happens in one place |
| Encapsulation    | Weak; internal state is exposed            | Strong; internal state is hidden     |

## The object-oriented approach: telling

In "tell-style" architecture, the caller simply informs the object of its
intent. The object, which owns the data, is responsible for deciding whether
the action is valid and how to update its internal state.

### Example: processing a bank withdrawal

**Asking (bad):**

```java
if (account.getBalance() >= amount) {
    account.setBalance(account.getBalance() - amount);
} else {
    throw new InsufficientFundsException();
}
```

The caller is doing the bank's job. If the logic for "overdraft protection"
changes, every piece of code that handles withdrawals must be updated.

**Telling (good):**

```java
account.withdraw(amount);
```

The `Account` object handles the balance check, the subtraction, and the
business rules internally. The caller doesn't need to know how a withdrawal
works, only that it is possible.

## Benefits for code quality

### Stronger encapsulation

TDA forces data to stay private. By removing getters and setters, the internal
representation of an object is shielded. This prevents "leaky abstractions"
where implementation details accidentally become part of the public API.

### Improved cohesion

Cohesion measures how closely related the responsibilities of a module are. TDA
increases cohesion by ensuring that logic governing a piece of data lives
exactly where that data is defined.

### Reduced train wrecks

Following TDA naturally leads to compliance with the Law of Demeter. Instead of
reaching through an object to find its "friends" to ask questions
(`user.getProfile().getPreferences().getTheme()`), simply tell the top-level
object what is needed (`user.applyTheme()`).

### Simplified testing

When an object handles its own logic, unit tests can focus on that object's
behavior in isolation. Callers become easier to test because they only need to
verify that a specific method was "told" to execute, not mock complex chains
of data retrieval.

## When to break the rule

There are specific contexts where "asking" is appropriate:

- **Data transfer objects (DTOs):** Objects designed to move data across
  boundaries (API responses, database rows) are meant to be "asked" for data
- **Functional programming:** In purely functional paradigms, data and behavior
  are intentionally separated
- **User interfaces:** UIs often need to "ask" an object for its state to
  display it. The goal is ensuring the UI doesn't contain the logic for
  modifying that state

## Related

- [[law-of-demeter]] - TDA is the practical application of LoD
- [[abstraction]] - Strong interfaces enable TDA
- [[triad-of-maintainability]] - TDA improves all three aspects
