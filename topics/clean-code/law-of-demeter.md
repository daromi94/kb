# Law of Demeter

Source: Codely

The Law of Demeter (LoD) is a design guideline for developing software,
particularly object-oriented programs. It states that a unit should have only
limited knowledge about other units: only units "closely" related to the
current unit.

In simpler terms: **"Only talk to your immediate friends; don't talk to
strangers."**

## The "train wreck" anti-pattern

The most common sign of a Law of Demeter violation is a long chain of method
calls, often called a "train wreck."

**Violation example:**

```java
customer.getWallet().getPaymentCard().charge(amount);
```

The calling code knows too much. It knows that a `Customer` has a `Wallet`,
that the `Wallet` contains a `PaymentCard`, and that the `PaymentCard` has a
`charge` method. If the structure of the `Wallet` changes (e.g., the customer
now uses a digital `PaymentService`), this code breaks.

## The formal rules

A method M of an object O may only invoke methods of:

1. **The object O itself:** Calling its own internal methods
2. **M's parameters:** Objects passed directly into the method
3. **Objects created within M:** Any object instantiated locally
4. **O's direct components:** Objects that are O's instance variables (fields)

The method should **not** invoke methods on objects returned by any of the
allowed calls (don't talk to the friends of your friends).

## The paperboy and the wallet

Imagine a paperboy comes to the door to collect payment.

- **LoD violation:** The paperboy reaches into the customer's pocket, pulls out
  their wallet, opens it, and takes out the exact change.
- **LoD compliance:** The paperboy asks the customer for the money. The
  customer interacts with their own wallet and hands the money to the paperboy.

In the compliant version, the paperboy doesn't need to know if the customer
keeps money in a wallet, a jar, or a pocket. The paperboy only knows how to
interact with the `Customer` interface.

## Impact on code quality

| Benefit                 | Explanation                                                            |
| ----------------------- | ---------------------------------------------------------------------- |
| Reduced coupling        | Classes are less dependent on internal structure of other classes      |
| Increased maintainability | Changes to one part (like `Wallet`) don't ripple through the codebase |
| Easier testing          | Fewer "stranger" dependencies makes mocking simpler                    |
| Lower WTFs/minute       | Code intent is clearer via "tell, don't ask" philosophy                |

## Tell, don't ask

The Law of Demeter is closely related to the "tell, don't ask" principle.
Instead of asking an object for its internal data to do something with it,
tell the object what you want it to do.

- **Asking (bad):** `if (engine.getOil().getPressure() < 10) { alert(); }`
- **Telling (good):** `if (engine.isOilPressureLow()) { alert(); }`

In the "telling" version, the `Engine` handles the logic of what constitutes
"low pressure," encapsulating that knowledge and keeping calling code clean.

## Exceptions and nuance

The Law of Demeter is a guideline, not a strict law. It generally does **not**
apply to:

- **Data structures:** Simple objects that only hold data (POJOs/DTOs) are
  meant to expose their internal structure
- **Fluent interfaces/builders:** Chaining like `builder.setName("X").setAge(20).build()`
  is not a violation because methods return the same context (the builder
  itself), not "stranger" objects

## Related

- [[tell-dont-ask]] - The practical application of LoD
- [[abstraction]] - Proper interfaces enable LoD compliance
