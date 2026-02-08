# Concepts

Foundational techniques and principles for distributed systems.

## Notes

- [Write-ahead log](write-ahead-log.md) - Durability through sequential logging
- [Segmented log](segmented-log.md) - Breaking WAL files into manageable segments
- [Bloom filters](bloom-filters.md) - Probabilistic data structure for set membership
- [Control plane vs data plane](control-plane-data-plane.md) - Separating configuration from request processing
- [Separate compute from data](separate-compute-from-data.md) - Decoupling compute and storage layers for independent
  scaling
- [Stateless vs stateful](stateless-vs-stateful.md) - How state retention affects scaling and recovery
- [Replication](replication.md) - Strategies and patterns for copying data across nodes
- [Partitioning](partitioning.md) - Splitting datasets across nodes for scalability
- [Low-water mark](low-water-mark.md) - Safe deletion boundary for segmented log cleanup
- [CAP theorem](cap-theorem.md) - Consistency, availability, and partition tolerance trade-offs
- [Leader and followers](leader-and-followers.md) - Single-leader coordination for total ordering of writes
- [Leader election](leader-election.md) - Choosing and replacing the cluster coordinator
- [Quorum and linearizability](quorum-and-linearizability.md) - Why quorum overlap alone does not guarantee strong
  consistency

---

Return to [Distributed Systems](../_index.md)
