# Abstraction

Source: Codely

Abstraction is the process of hiding underlying implementation details and
exposing only essential features. It is a tool for "selective ignorance,"
allowing a developer to interact with a complex system without understanding
every internal moving part simultaneously.

By hiding irrelevant complexity, abstraction allows the human mind to reason
about systems that would otherwise be cognitively overwhelming.

## The process vs the entity

Abstraction works in two directions:

- **Generalization:** Identifying commonalities between different objects and
  creating a single representation to cover all cases
- **Detail hiding (encapsulation):** Obscuring the implementation "how" to
  focus on the functional "what"

In a clean codebase, a well-defined abstraction acts as a "contract." As long
as inputs and outputs remain consistent, the internal machinery can be swapped
or optimized without breaking the surrounding system.

## Levels of abstraction

Abstraction functions like a hierarchy. Each level provides a simplified
interface to the level below it. Well-abstracted code follows the **single
level of abstraction principle**: all statements within a function should be
at the same conceptual level.

| Level      | Example                          | Focus                                  |
| ---------- | -------------------------------- | -------------------------------------- |
| High level | `order.process()`                | Business logic and "what" is happening |
| Mid level  | `paymentGateway.charge(amount)`  | Integration logic and orchestration    |
| Low level  | `socket.send(buffer)`            | Technical implementation and "how"     |

## Benefits for code quality

- **Readability:** Replacing a complex 50-line algorithm with a well-named
  function call like `validateUserCredentials()` makes intent immediately clear
- **Reduced cognitive load:** The brain can only hold about seven pieces of
  information in short-term memory. Abstraction "chunks" information, allowing
  understanding of a system as interacting boxes rather than tangled lines
- **Decoupling for modification:** If implementation details of a "black box"
  change (e.g., switching from SQL to NoSQL), the code that uses that box
  remains untouched as long as the public interface stays the same

## The automotive analogy

A driver interacts with a car through steering wheel, pedals, and gear shifter.
This is the abstraction layer. The driver doesn't need to understand internal
combustion or fuel injection to navigate. If the engine is replaced with an
electric motor, the abstraction remains the same, so the driver doesn't need
to learn a new way to drive.

## Low vs high abstraction in code

**Low abstraction (high WTF potential):** Code manually opens an SMTP
connection, authenticates with base64, constructs a MIME header, and handles
packet retries. If the notification method changes to SMS, this entire block
must be ripped out.

**High abstraction (clean):** The developer calls
`NotificationService.send(message, recipient)`. Whether it uses email, SMS, or
Slack is hidden behind the service.

## The danger of over-abstraction

**Leaky abstractions** occur when implementation details "leak" through to the
user. **Over-abstraction** (creating layers for the sake of layers) leads to
"boilerplate hell," where a developer must navigate through five different
files just to find where a single line of logic executes.

## Relationship to cognitive load

Abstraction is the primary tool for keeping the WTF/minute count low:

1. **Reduced specification:** By focusing on high-level models, the amount of
   code a developer must hold in working memory is reduced
2. **Increased modifiability:** When code depends on abstractions (interfaces)
   rather than concretions (specific classes), the system becomes "pluggable"
3. **Language of the business:** Abstraction allows code written in the
   "ubiquitous language" of the problem domain (e.g., `policy.calculatePremium()`)
   rather than the language of the machine (e.g., `float result = (x * 0.05) + y`)

## Related

- [Indirection](indirection.md) - Closely related but serves different purpose
- [Polymorphism](polymorphism.md) - Uses abstraction for dynamic behavior
- [WTFs per minute](wtfs-per-minute.md) - What abstraction helps minimize
