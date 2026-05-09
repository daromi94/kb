# Stateless vs stateful

Whether a process maintains information about previous interactions across
requests determines how it scales, recovers from failure, and integrates
with the rest of a distributed system.

## Stateless processes

A stateless process treats every request as a brand-new interaction with no
locally stored context.

- **Self-contained requests** — Each request carries all necessary context
  (authentication tokens, user IDs, data snapshots)
- **Linear scale-out** — Any instance is interchangeable; a load balancer
  can route to any available node
- **Instant recovery** — A failed node is replaced without data recovery or
  sync; the source of truth lives elsewhere

**Example:** A REST API that converts currencies. It takes input, computes
a result, and returns it without remembering the caller.

## Stateful processes

A stateful process maintains a memory of previous events. Its current state
depends on the sequence of operations that preceded it.

- **Contextual dependency** — Processing a withdrawal requires knowing the
  balance from all previous deposits
- **Complex scaling** — Adding a node requires state transfer to bring it
  up to date before it can serve requests
- **Durability responsibility** — Uses patterns like the write-ahead log to
  reconstruct state after a restart

**Example:** A database (Cassandra), a message broker (Kafka), or a TCP
connection tracking sequence numbers and window sizes.

## Comparison

| Feature    | Stateless                | Stateful                      |
|------------|--------------------------|-------------------------------|
| Storage    | No local persistence     | Local disk or memory state    |
| Scaling    | Horizontal (elastic)     | Vertical or sharded (complex) |
| Dependency | Requests are independent | Requests depend on history    |
| Failure    | Disposable (cattle)      | Requires recovery (pets)      |
| Metadata   | Passed in the request    | Stored in the system          |

## Relationship to compute/data separation

Separating compute from data turns the compute layer into a stateless
service and the storage layer into a stateful service:

1. The compute node fetches required state from storage
2. It performs logic statelessly
3. It pushes updated state back to the storage layer

This lets the compute layer scale elastically while the storage layer
focuses on consistency and consensus.

---

Return to [Concepts](_index.md)
