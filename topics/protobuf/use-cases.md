# Use Cases

Protobuf is designed for both ephemeral data (RPC calls) and persistent storage
(disk). Its efficiency makes it suitable for high-performance and
resource-constrained environments.

## gRPC

Protobuf is the default serialization format for Google's high-performance RPC
framework. Service interfaces are defined in `.proto` files alongside message
types.

## Microservices

Reduces latency and bandwidth in inter-service communication. The binary format
and code generation eliminate the overhead of text parsing and runtime schema
validation.

## Large-Scale Storage

Saves disk space when storing billions of structured records. The compact binary
format provides significant savings over JSON or XML for archival data.

## Mobile and IoT

Efficient data transfer for devices with limited bandwidth or battery life.
Smaller payloads mean less radio time and lower power consumption.

## When to Use Protobuf

| Scenario                           | Fit   |
|------------------------------------|-------|
| High-traffic service communication | Good  |
| Long-term data archival            | Good  |
| Bandwidth-constrained devices      | Good  |
| Browser-based web APIs             | Poor  |
| Human-readable debugging needs     | Poor  |
| Rapidly changing schemas           | Mixed |

## Related

- [Architecture](architecture.md) - Component model and JSON comparison
- [Wire format](wire-format.md) - How efficiency is achieved
