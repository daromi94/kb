# Design by contract

A software correctness methodology where components interact through
formal, enforceable specifications rather than implicit trust.
Invented by Bertrand Meyer, formalized in Eiffel and
*Object-Oriented Software Construction*. The metaphor is from
business law: two parties enter an agreement with explicit mutual
obligations and benefits.

## The three components

Every function has a contract defined by three elements.

**Preconditions** are the caller's obligations. They define what must
be true before the function executes. A caller that violates a
precondition has a bug — the function must not try to handle it
gracefully.

```text
function binary_search(list, target)
    require: list is sorted
    require: list is not empty
```

**Postconditions** are the function's guarantee. They define what
must be true when it returns, provided preconditions were met. A
function that violates its postcondition has a bug. Postconditions
make behavior verifiable — the implementation could be swapped
entirely as long as the contract still holds.

```text
function binary_search(list, target)
    require: list is sorted
    require: list is not empty
    ensure:  result == -1 or list[result] == target
    ensure:  result == -1 implies target not in list
```

**Class invariants** are properties that hold for every instance at
every stable point — after construction and after every public method
call. Invariants may temporarily break during internal computation
but must be restored before control returns to the caller.

```text
class SortedList
    invariant: for all i in 0..length-2, items[i] <= items[i+1]
    invariant: length >= 0
```

## Fault isolation

Contract violations are not runtime exceptions to catch and manage.
A broken contract is a logic defect in source code. Execution halts
immediately, and the assertion trace pinpoints which side failed.

| Violation            | Defect location          |
|----------------------|--------------------------|
| Precondition broken  | The caller has a bug     |
| Postcondition broken | The function has a bug   |
| Invariant broken     | The last method that ran |

Without contracts, a crash in function G might be caused by bad data
introduced in function A and passed undetected from B through F.

## The subcontracting rule

When a subclass overrides a method, the contract must obey:

| Element        | Allowed change                        |
|----------------|---------------------------------------|
| Preconditions  | Weaken or keep equal, never tighten   |
| Postconditions | Strengthen or keep equal, never relax |
| Invariants     | Strengthen or keep equal, never relax |

A subclass can accept more inputs (weaker preconditions) and
guarantee more about its output (stronger postconditions), but never
the reverse. This is the Liskov Substitution Principle expressed
formally: if code works with a parent type, it must work with any
subtype.

The classic violation: Square extending Rectangle with an invariant
that `width == height`. Setting width on a Square must also set
height, violating the postcondition callers expect from
`setWidth()` — namely that only width changes. Contract analysis
reveals Square is not a valid subtype of Rectangle despite the
"is-a" intuition.

## DbC vs defensive programming

Both involve checking conditions, but the philosophies differ.

Defensive programming says: "I don't trust my caller, so I'll check
everything and try to handle bad input gracefully." This can mask
bugs — silently sorting an unsorted list hides a defect in the
calling code. The symptom appears far from the cause.

DbC says: "My caller and I have an agreement. Violating it is a bug,
and the correct response is to report it immediately, not mask it."

In practice, well-designed systems use both. DbC governs internal
interfaces where both sides are under the same team's control.
Defensive programming governs external boundaries — user input, API
endpoints, third-party integrations — where the caller cannot be
trusted and crashing is not acceptable.

## Contracts vs types

Type systems and contracts sit on a spectrum of expressiveness. A
type like int establishes a weak contract. A type like PositiveInt
strengthens it. But most type systems cannot express "the output list
has the same elements as the input in sorted order" or "the balance
after withdrawal equals the old balance minus the amount."

Dependent type systems (Idris, Agda) blur this boundary by encoding
contracts directly in types, checked at compile time. For mainstream
languages, contracts remain a runtime concern enforced through
assertions or contract libraries.

## Practical implications

**Design:** Write the contract before the implementation. This forces
clarity about what the function requires and promises. Many design
mistakes are obvious at the contract level but invisible at the
implementation level.

**Documentation:** Contracts are executable documentation. They
cannot go stale like comments because they run as part of the
program.

**Testing:** Contracts and tests are complementary. Tests verify
specific scenarios; contracts verify properties across all
executions. Contracts catch bugs no finite test suite covers.

## Limitations

Contracts cannot express performance characteristics, eventual
consistency, probabilistic properties, or timing constraints.
They add runtime overhead when enforced, though they can be disabled
in production. Overly weak contracts miss bugs; overly strong
contracts reject valid inputs or constrain future implementations.

The biggest barrier is cultural. Most languages lack first-class
contract support, so contracts end up as assert statements easy to
ignore.

## Related

- [Defensive programming](defensive-programming.md) - Complementary approach for external boundaries

---

Return to [Correctness](_index.md)
