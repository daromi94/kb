# Concepts

Foundational techniques and principles for distributed systems.

## Notes

- [CAP theorem](cap-theorem.md) - Fundamental consistency trade-offs
- [Stateless vs stateful](stateless-vs-stateful.md) - State and scaling implications
- [Separate compute from data](separate-compute-from-data.md) - Decoupling compute and storage
- [Distributed monolith](distributed-monolith.md) - Coupled services antipattern
- [Control plane vs data plane](control-plane-data-plane.md) - Configuration vs request processing
- [Replication](replication.md) - Multi-node data copying
- [Partitioning](partitioning.md) - Splitting data across nodes
- [Leader and followers](leader-and-followers.md) - Single-leader write coordination
- [Heartbeat](heartbeat.md) - Periodic liveness signaling
- [Failure detection at scale](failure-detection-at-scale.md) - Heartbeat topology at scale
- [Leader election](leader-election.md) - Choosing the cluster coordinator
- [Quorum](quorum.md) - Minimum agreement for operations
- [Quorum and linearizability](quorum-and-linearizability.md) - Quorum overlap and consistency
- [Write-ahead log](write-ahead-log.md) - Durability through sequential logging
- [Segmented log](segmented-log.md) - Splitting WAL into segments
- [Low-water mark](low-water-mark.md) - Safe log deletion boundary
- [Bloom filters](bloom-filters.md) - Probabilistic set membership

---

Return to [Distributed systems](../_index.md)
