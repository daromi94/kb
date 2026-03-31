# Abstraction

Abstraction is the process of hiding underlying implementation details and
exposing only essential features. It is a tool for selective ignorance,
allowing a developer to interact with a complex system without understanding
every internal moving part simultaneously. A well-defined abstraction acts as
a contract: as long as inputs and outputs remain consistent, the internal
machinery can be swapped or optimized without breaking the surrounding system.

## Two directions

Abstraction works in two directions:

- **Generalization:** Identifying commonalities between different objects and
  creating a single representation to cover all cases
- **Detail hiding:** Obscuring the implementation "how" to focus on the
  functional "what." Parnas called this information hiding: a module exposes
  a narrow interface and keeps everything else private

## Levels of abstraction

Abstraction functions like a hierarchy. Each level provides a simplified
interface to the level below it: TCP hides the unreliability of IP, a file
system hides raw disk blocks, an ORM hides SQL. Each layer translates a
detail-rich reality into a more convenient model, letting you reason about
one layer without thinking about the ones below it.

The same principle applies at the code level. The **single level of
abstraction principle** states that all statements within a function should
be at the same conceptual level.

| Level      | Example                         | Focus                                  |
|------------|---------------------------------|----------------------------------------|
| High level | `order.process()`               | Business logic and "what" is happening |
| Mid level  | `paymentGateway.charge(amount)` | Integration logic and orchestration    |
| Low level  | `socket.send(buffer)`           | Technical implementation and "how"     |

## Benefits

- **Readability:** Even naming is a micro-abstraction — replacing a complex
  algorithm with `validateUserCredentials()` lets the reader skip the body
  and trust the name
- **Reduced cognitive load:** Abstraction chunks information, allowing
  understanding of a system as interacting boxes rather than tangled lines
- **Decoupling:** When code depends on abstractions (interfaces) rather than
  concretions (specific classes), the system becomes pluggable. If
  implementation details change (e.g., switching from SQL to NoSQL), consumers
  remain untouched as long as the public interface stays the same
- **Domain language:** Abstraction allows code written in the ubiquitous
  language of the problem domain (e.g., `policy.calculatePremium()`) rather
  than the language of the machine (e.g., `float result = (x * 0.05) + y`)

## Low vs high abstraction in code

**Low abstraction:** Code manually opens an SMTP connection, authenticates
with base64, constructs a MIME header, and handles packet retries. If the
notification method changes to SMS, this entire block must be ripped out.

**High abstraction:** The developer calls
`NotificationService.send(message, recipient)`. Whether it uses email, SMS, or
Slack is hidden behind the service.

## Related

- [Leaky abstractions](leaky-abstractions.md) - When hidden complexity surfaces
- [Premature abstraction](premature-abstraction.md) - Costs of abstracting too early
- [Indirection](indirection.md) - Closely related but serves different purpose
- [Polymorphism](polymorphism.md) - Uses abstraction for dynamic behavior

---

Return to [Principles](_index.md)
