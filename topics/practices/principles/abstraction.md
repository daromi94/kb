# Abstraction

Hiding implementation details behind a narrow interface. A well-defined
abstraction is a contract: as long as inputs and outputs stay consistent,
internals can change without breaking consumers.

## Two directions

- **Generalization:** Extract commonalities into a single representation
  that covers all cases
- **Detail hiding:** Expose the "what," conceal the "how." Parnas called
  this information hiding — a module keeps everything behind its interface
  private

## Levels

Abstraction forms a hierarchy. Each level simplifies the one below it: TCP
hides the unreliability of IP, a file system hides raw disk blocks, an ORM
hides SQL.

The **single level of abstraction principle** says every statement in a
function should sit at the same conceptual level:

| Level | Example                         | Focus                    |
|-------|---------------------------------|--------------------------|
| High  | `order.process()`               | Business intent ("what") |
| Mid   | `paymentGateway.charge(amount)` | Orchestration            |
| Low   | `socket.send(buffer)`           | Technical ("how")        |

## Why it matters

- **Readability.** A name like `validateCredentials()` lets the reader skip
  the body and trust the label — naming is micro-abstraction
- **Cognitive load.** Systems become interacting boxes instead of tangled
  lines
- **Decoupling.** Depend on interfaces, not concretions — swap SQL for
  NoSQL without touching consumers
- **Domain language.** `policy.calculatePremium()` speaks the problem
  domain; `float result = (x * 0.05) + y` speaks the machine

## Low vs high abstraction

Low: manually open an SMTP connection, base64-authenticate, build a MIME
header, retry on failure. Changing to SMS means ripping out the entire block.

High: call `NotificationService.send(message, recipient)`. Email, SMS, or
Slack is hidden behind the service.

## Related

- [Leaky abstractions](leaky-abstractions.md) - When hidden complexity surfaces
- [Premature abstraction](premature-abstraction.md) - Costs of abstracting too early
- [Indirection](indirection.md) - Closely related but serves different purpose
- [Polymorphism](polymorphism.md) - Uses abstraction for dynamic behavior

---

Return to [Principles](_index.md)
