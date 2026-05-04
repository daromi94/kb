# Operational lessons

Principles distilled from a decade of running DynamoDB at massive scale.
Each addresses a specific challenge in maintaining stability and
durability.

## Adaptive partitioning

Static partitioning assumes uniform access, but real workloads are
skewed. DynamoDB moved from splitting partitions only by size to
splitting by consumed throughput. The system observes key distribution
and access patterns, then reshapes partitions to eliminate hot spots
that would otherwise throttle applications.

## Continuous verification

Durability is a continuous process, not a one-time property. A
background scrub process detects silent data corruption by verifying
two things:

1. All three replicas in a replication group are identical.
2. Live replicas match a reference replica built offline from
   write-ahead logs archived to S3.

This catches hardware bit rot and subtle software bugs that might go
undetected until data is read.

## Formal methods and deployment safety

Complex distributed protocols are hard to test exhaustively. DynamoDB
verifies its Multi-Paxos replication protocol with TLA+ specifications
to catch logic errors that manual testing would miss.

Deployments use a two-phase read-write strategy: new software that
reads the updated state is deployed first and verified, then software
that produces the updated state follows. This ensures old and new
message formats coexist safely during rollouts. Game days (intentional
failure injection) validate that automated recovery works under stress.

## Predictability over efficiency

Caches create bimodal behavior — fast when hot, catastrophic when
cold. DynamoDB eliminates this by keeping constant load on backing
infrastructure regardless of cache state. In MemDS, even a local cache
hit triggers an asynchronous backend call. The system is always
provisioned for the "worst case," so a cache failure never causes a
traffic surge the backend cannot absorb.

## Related

- [Performance](performance.md) - Latency and admission control

---

Return to [DynamoDB](_index.md)
