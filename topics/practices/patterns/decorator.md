# Decorator

A structural pattern that adds behavior to individual objects by wrapping
them in decorator objects that share the same interface. Decorators
compose at runtime, avoiding the combinatorial explosion of subclasses
that static inheritance produces.

## Structure

Four roles make up the pattern:

| Role               | Purpose                                        |
|--------------------|------------------------------------------------|
| Component          | Interface defining operations for all objects  |
| Concrete Component | The core object receiving new behavior         |
| Base Decorator     | Implements Component, delegates to the wrapped |
| Concrete Decorator | Overrides methods to inject behavior           |

A data source decorated with encryption and compression:

```text
+---------------------+
|    <<Component>>    |
|   writeData(data)   |
|   readData(): data  |
+---------------------+
        ^         ^
        |         |
+------------+  +---------------------+
| FileData   |  | DataSourceDecorator |
| Source     |  |  wraps: Component   |
+------------+  +---------------------+
                          ^
              +-----------+-----------+
              |                       |
  +---------------------+  +----------------------+
  | EncryptionDecorator |  | CompressionDecorator |
  +---------------------+  +----------------------+
```

The same example in pseudocode:

```text
interface DataSource:
    method writeData(data)
    method readData(): data

class FileDataSource implements DataSource:
    constructor(filename)
    method writeData(data)
    method readData(): data

class DataSourceDecorator implements DataSource:
    field wrapper: DataSource

    constructor(source: DataSource):
        this.wrapper = source

    method writeData(data):
        this.wrapper.writeData(data)

    method readData(): data:
        return this.wrapper.readData()

class EncryptionDecorator extends DataSourceDecorator:
    method writeData(data):
        super.writeData(encrypt(data))

    method readData(): data:
        return decrypt(super.readData())

class CompressionDecorator extends DataSourceDecorator:
    method writeData(data):
        super.writeData(compress(data))

    method readData(): data:
        return decompress(super.readData())

// Compose at runtime:
source = FileDataSource("data.txt")
source = EncryptionDecorator(source)
source = CompressionDecorator(source)
source.writeData("application data")
```

## Design guidelines

**Keep the Component interface lean.** A wide interface forces every
decorator to implement boilerplate delegation for methods it does not
alter. Segregate large interfaces into smaller contracts before applying
the pattern.

**Use interfaces, not abstract base classes with state.** State in the
base component leaks into every decorator, causing memory overhead and
unintended side effects.

**Program to the interface.** Never add public methods to a decorator
that the Component interface does not define. If client code must
downcast to a specific decorator, the pattern has failed.

**Honor the original contract.** Decorators must preserve the semantic
guarantees of the base component — return types, exception behavior,
and invariants.

**Prefer stateless decorators.** A decorator should perform its
operation (logging, auth, compression) and delegate immediately. If
state is unavoidable, guard against conflicts with the wrapped
component's state and against race conditions under concurrency.

**Codify decoration order.** The sequence of wrapping changes
correctness — compressing before encrypting is standard; encrypting
before compressing renders compression useless. Enforce order in a
Factory or Builder, not in calling code.

**Hide instantiation behind factories.** As chains grow, manual
construction becomes brittle. A Factory or Builder centralizes the
wrapping order and keeps client code decoupled.

## Trade-offs

| Benefit                                                | Cost                                                    |
|--------------------------------------------------------|---------------------------------------------------------|
| Extends behavior without modifying existing code (OCP) | Decorated object loses identity — equality checks break |
| Combines behaviors at runtime                          | Deep wrapper stacks obscure debugging                   |
| Single-purpose decorator classes (SRP)                 | Many small, similar classes                             |
| Avoids subclass explosion                              | Order sensitivity can cause subtle bugs if not enforced |

## Common applications

**I/O streams.** A raw byte stream wraps in a buffer, then an encoding
layer, then compression — each layer a decorator around the previous.

**HTTP middleware.** A base handler wraps in logging, authentication,
and tracing decorators. Each processes the request or response before
delegating inward.

**Network resiliency.** A base RPC client decorates with retry, circuit
breaker, and timeout layers.

**UI components.** Visual elements wrap in scrollbar, border, or shadow
decorators without altering the base drawing logic.

## Related

- [Flyweight](flyweight.md) - Decorator adds behavior, Flyweight shares state

---

Return to [Patterns](_index.md)
