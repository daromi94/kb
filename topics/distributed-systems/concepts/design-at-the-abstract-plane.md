# Design at the abstract plane

Design a distributed system in terms of state, transitions, and
invariants. At that level, alternatives are visible and correctness can
be reasoned about.

Settle the design at this level before writing code. Code locks in one
specific implementation and obscures the alternatives.

## Abstraction is precision, not vagueness

An abstract model defines its state, transitions, and invariants
precisely. It is smaller than the real system because irrelevant
details are omitted, not because it is vaguer.

Dijkstra: *"The purpose of abstraction is not to be vague, but to
create a new semantic level in which one can be absolutely precise."*

Tools that enforce this precision include TLA+, IO automata, and
process calculi. Careful prose with pre/postconditions works too.

## Canonical abstractions

| Abstraction     | Hides                                           | Exposes                        |
|-----------------|-------------------------------------------------|--------------------------------|
| MapReduce       | Scheduling, partitioning, retries, stragglers   | Two pure functions, a shuffle  |
| Dataflow DAG    | Operator placement, fusion, recovery            | Operator graph with contracts  |
| Log             | Replication, leader handoff, storage layout     | Append, offset, read           |
| Linearizability | Quorums, replication timing, message reordering | Single-copy register semantics |

## The implementation can drift from the model

The model assumes things the real system doesn't deliver: operations
that aren't atomic, messages that aren't instantaneous, schedules that
aren't fair. Most bugs live in this gap between model and code.

Two practices close it:

- **Deterministic simulation.** Run the implementation under controlled
  scheduling and injected faults to exercise the interleavings the
  model permits
- **Conformance testing.** Check the implementation's observable
  behavior against the spec

---

Return to [Concepts](_index.md)
