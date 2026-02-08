# Concepts

Foundational techniques and principles for distributed systems.

## Notes

- [CAP theorem](cap-theorem.md) - Consistency, availability, and partition tolerance trade-offs
- [Stateless vs stateful](stateless-vs-stateful.md) - How state retention affects scaling and recovery
- [Control plane vs data plane](control-plane-data-plane.md) - Separating configuration from request processing
- [Separate compute from data](separate-compute-from-data.md) - Decoupling compute and storage layers for independent
  scaling
- [Replication](replication.md) - Strategies and patterns for copying data across nodes
- [Partitioning](partitioning.md) - Splitting datasets across nodes for scalability
- [Leader and followers](leader-and-followers.md) - Single-leader coordination for total ordering of writes
- [Heartbeat](heartbeat.md) - Periodic liveness signal, timing inequality, and lease renewal
- [Failure detection at scale](failure-detection-at-scale.md) - How heartbeat topology changes from small to large
  clusters
- [Leader election](leader-election.md) - Choosing and replacing the cluster coordinator
- [Quorum](quorum.md) - The intersection rule, common configurations, and strict vs sloppy quorum
- [Quorum and linearizability](quorum-and-linearizability.md) - Why quorum overlap alone does not guarantee strong
  consistency
- [Write-ahead log](write-ahead-log.md) - Durability through sequential logging
- [Segmented log](segmented-log.md) - Breaking WAL files into manageable segments
- [Low-water mark](low-water-mark.md) - Safe deletion boundary for segmented log cleanup
- [Bloom filters](bloom-filters.md) - Probabilistic data structure for set membership

---

Return to [Distributed Systems](../_index.md)
