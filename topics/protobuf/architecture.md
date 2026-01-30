# Architecture

Protobuf is an integrated ecosystem consisting of four distinct layers.

## Component Layers

**Definition Language (IDL):** The `.proto` file. A platform-independent schema
used to define data structures (messages) and service interfaces.

**Proto Compiler (`protoc`):** A build-time tool that parses `.proto` files and
generates source code (native bindings) for specific programming languages
(C++, Java, Python, Go, and others).

**Runtime Libraries:** Language-specific libraries required to handle the
underlying logic of encoding and decoding the binary stream.

**Wire Format:** The compact binary representation of the data transmitted over
a network or stored on disk.

## Native Language Bindings

Unlike JSON, which requires manual mapping or reflection-based parsing at
runtime, Protobuf uses code generation:

- Developers interact with generated classes or structs
- Methods like `SerializeToString()` or `ParseFromString()` are pre-compiled
- This eliminates CPU overhead from parsing strings and validating schemas
  during execution

## Technical Neutrality

**Language-Neutral:** A service written in Java can communicate with a service
in C++ using the same `.proto` definition. The binary wire format remains
identical regardless of implementation language.

**Platform-Neutral:** The serialization logic is independent of CPU architecture
(endianness) or operating system.

## Comparison with JSON

| Feature          | JSON                         | Protocol Buffers               |
|------------------|------------------------------|--------------------------------|
| Format           | Text (human-readable)        | Binary (machine-optimized)     |
| Schema           | Optional / implicit          | Mandatory (`.proto`)           |
| Data binding     | Runtime parsing              | Build-time code generation     |
| Payload size     | Large (includes keys/braces) | Minimal (tags and values only) |
| Performance      | High CPU overhead            | Low CPU overhead               |
| Interoperability | Native to web/browsers       | Requires generated bindings    |

## Related

- [Wire format](wire-format.md) - How binary encoding achieves efficiency
- [Schema evolution](schema-evolution.md) - How compatibility is maintained
