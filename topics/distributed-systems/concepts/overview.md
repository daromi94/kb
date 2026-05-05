# Overview

A distributed system is a collection of independent computers that
communicate over an unreliable network to appear as one coherent
service. Clients see a single logical entity — state management,
coordination, and network communication are hidden behind that
abstraction.

- **Behavior** emerges from the behavior of each component and the
  interactions between them.
- **Complexity** emerges from the complexity of each component and
  the intricacy of those interactions.

The primary domain is foundational infrastructure: distributed file
systems, coordination services, key-value databases, and
batch-processing engines.

## Engineering challenges

**Concurrency.** Operations run simultaneously across nodes whose
clocks are not synchronized. Maintaining consistency requires
distributed transactions, concurrency control, or carefully designed
eventual consistency models.

**Non-deterministic interactions.** Messages can arrive out of order,
get dropped, or interleave in countless ways. This makes system
behavior unpredictable and exhaustive testing impossible.

**Communication overhead.** Adding machines introduces unavoidable
costs: network round-trips, serialization, and consensus protocol
latency. These bottlenecks can negate the gains of extra hardware.

**Partial failure.** The defining characteristic of distributed
computing. A single machine typically fails completely (fail-stop). A
distributed system experiences localized failures constantly — some
nodes reachable, others partitioned, others degraded. The system must
handle these mixed states without halting global progress.

## Why distribute

**Capacity.** A single machine has finite CPU, memory, and bus
bandwidth. Sharding data and spreading computation across many
machines enables near-linear horizontal scaling.

**Fault tolerance.** Hardware fails continuously at scale. Replicating
state across independent failure domains and using consensus protocols
(Paxos, Raft) masks node or rack failures from clients.

**Locality.** Network signals have a hard latency floor set by the
speed of light — a round-trip from New York to Tokyo takes at least
~67ms regardless of optimization. Placing nodes close to where data
is generated or consumed avoids that penalty and the bandwidth cost
of moving large datasets across continents.

**Isolation.** Separating services across machines enforces security
and operational boundaries. A compromised node, kernel panic, or
memory leak is physically contained, limiting blast radius.

## Related

- [Emergence](emergence.md) - Behavior arising from local interactions
- [CAP theorem](cap-theorem.md) - Fundamental consistency trade-offs
- [Replication](replication.md) - Multi-node data copying
- [Partitioning](partitioning.md) - Splitting data across nodes

---

Return to [Concepts](_index.md)
