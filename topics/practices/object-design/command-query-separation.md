# Command-query separation

Command-query separation (CQS) states that every method should either be a
**command** that changes state or a **query** that returns data, but never
both. Asking a question should not change the answer.

Coined by Bertrand Meyer in *Object-Oriented Software Construction*.

## Commands and queries

**Query:** Returns a result without changing observable state. Safe to call
anywhere — in loops, logging, assertions — without side effects.

**Command:** Changes state but returns nothing (`void`). Signals to the
reader that this call mutates something, requiring attention to ordering
and concurrency.

The return type is the primary indicator: a method returning a value is a
query; a method returning `void` is a command.

## Observable vs internal state

CQS applies to **observable** state. A query may modify internal state if
the change is invisible to callers:

- **Memoization:** A query caches its result on first call. The object's
  memory changes, but the observable behavior is identical.
- **Lazy initialization:** A field is populated on first access. Subsequent
  calls see the same value.

## Classic violation: iterators

`iterator.next()` returns the current element (query) and advances the
pointer (command) in a single call. Under strict CQS, this splits into:

```java
iterator.current(); // query: return element at position
iterator.advance(); // command: move pointer forward
```

## When to break the rule

**Stack pop:** `stack.pop()` returns the top element and removes it.
Splitting into `top()` and `remove()` is possible but less intuitive for
this data structure.

**Atomic operations:** In concurrent code, separating a check from an act
creates race conditions. `getAndIncrement()` must combine query and command
to guarantee atomicity.

## CQS vs CQRS

| Scope  | CQS                                 | CQRS                                         |
|--------|-------------------------------------|----------------------------------------------|
| Level  | Individual methods within a class   | System architecture                          |
| Action | Separate return value from mutation | Separate read and write models or datastores |

CQRS applies the same separation at architectural scale, often using
different databases for reads and writes.

---

Return to [Object design](_index.md)
