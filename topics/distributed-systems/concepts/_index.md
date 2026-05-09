# Concepts

Foundational techniques and principles for distributed systems.

## Notes

- [Overview](overview.md) - Definition and motivation
- [Emergence](emergence.md) - Global behavior from local rules
- [State machine model](state-machine-model.md) - Discrete-step abstraction
- [CAP theorem](cap-theorem.md) - Fundamental consistency trade-offs
- [CALM theorem](calm-theorem.md) - Monotonicity and coordination
- [Stateless vs stateful](stateless-vs-stateful.md) - State and scaling implications
- [Separate compute from data](separate-compute-from-data.md) - Decoupling compute and storage
- [Control plane vs data plane](control-plane-data-plane.md) - Configuration vs request processing
- [Distributed monolith](distributed-monolith.md) - Coupled services antipattern
- [Crash or continue](crash-or-continue.md) - Error handling as architecture
- [Crash-only software](crash-only-software.md) - Structural properties for crash resilience
- [Blast radius reduction](blast-radius-reduction.md) - Containment through compartmentalization
- [Metastable failures](metastable-failures.md) - Self-sustaining failure states
- [Backpressure](backpressure.md) - Producer-consumer flow control
- [CoDel](codel.md) - Time-based load shedding
- [Replication](replication.md) - Multi-node data copying
- [Partitioning](partitioning.md) - Splitting data across nodes
- [Leader and followers](leader-and-followers.md) - Single-leader write coordination
- [Leader election](leader-election.md) - Choosing the cluster coordinator
- [Centralized task state](centralized-task-state.md) - Coordinator owns task lifecycle
- [Heartbeat](heartbeat.md) - Periodic liveness signaling
- [Failure detection at scale](failure-detection-at-scale.md) - Heartbeat topology at scale
- [Quorum](quorum.md) - Minimum agreement for operations
- [Quorum and linearizability](quorum-and-linearizability.md) - Quorum overlap and consistency
- [Write-ahead log](write-ahead-log.md) - Durability through sequential logging
- [Segmented log](segmented-log.md) - Splitting WAL into segments
- [Low-water mark](low-water-mark.md) - Safe log deletion boundary
- [Bloom filters](bloom-filters.md) - Probabilistic set membership

---

Return to [Distributed systems](../_index.md)
