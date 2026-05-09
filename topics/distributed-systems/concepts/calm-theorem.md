# CALM theorem

CALM (Consistency As Logical Monotonicity) states that a program has
a consistent, coordination-free distributed implementation if and only
if it is monotonic. It answers when a distributed system needs
coordination to stay consistent.

## Monotonicity

A monotonic program only adds to its output as new information
arrives — it never retracts or invalidates previous conclusions. Set
union is the canonical example: regardless of the order data arrives
from different nodes, the result is the same.

A non-monotonic program retracts previous output when new
information arrives. Set difference, deletions, negation, and
aggregations that require complete input (like a final count) are all
non-monotonic — new data can change a previously correct answer.

## The coordination boundary

Coordination protocols (Paxos, Raft, two-phase commit) force nodes
to pause and agree on state or ordering — the primary bottleneck for
latency and scalability.

CALM draws the line:

- **Monotonic logic** converges to a consistent result without
  coordination. Messages can arrive out of order, be duplicated, or
  be delayed, and nodes independently reach the same final state.
- **Non-monotonic logic** requires coordination. The system must
  establish a definitive order of events or confirm completeness
  before producing output.

## Practical implication

CALM shifts the design question from "how do we coordinate?" to
"which parts of our logic are monotonic?" Coordination overhead is
then isolated to the non-monotonic boundaries.

CRDTs (Conflict-free Replicated Data Types) are a direct application:
their merge operations are monotonic (commutative, associative,
idempotent), so replicas converge without coordination.

---

Return to [Concepts](_index.md)
