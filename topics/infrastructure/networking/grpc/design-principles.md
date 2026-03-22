# Design principles

Core design choices that shaped gRPC's architecture and scope.

## Services not objects

Promote coarse-grained message exchange between systems. Avoid the
pitfalls of distributed objects and the fallacy of ignoring the
network.

## Layered

Stack components evolve independently. Wire-format changes do not
disrupt application-layer bindings.

## Payload agnostic

Protocol Buffers are the default but not the only option. The
framework supports multiple encodings (JSON, XML, Thrift) and
pluggable compression.

## Lameducking

Servers shut down gracefully by rejecting new requests while
completing in-flight ones.

## Extensions as APIs

Cross-cutting concerns (health checking, load balancing, service
introspection) are exposed as APIs rather than protocol extensions.
This keeps the core protocol simple and lets extensions evolve
independently.

## Standardized status codes

The status code namespace is deliberately constrained to simplify
error handling. Richer domain-specific status travels through metadata
exchange.

---

Return to [gRPC](_index.md)
