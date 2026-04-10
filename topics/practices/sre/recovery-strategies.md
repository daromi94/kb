# Recovery strategies

Disaster recovery architectures map to points on the RTO/RPO
spectrum. Each strategy trades cost and complexity for tighter
recovery guarantees. Choosing the right one starts with the business
requirements, not the technology.

## Strategy comparison

| Strategy       | RTO         | RPO             | Cost    |
|----------------|-------------|-----------------|---------|
| Backup/restore | Hours–days  | Hours           | Lowest  |
| Pilot light    | Tens of min | Minutes–seconds | Low     |
| Warm standby   | Minutes     | Seconds         | Medium  |
| Active-active  | Near zero   | Near zero       | Highest |

## Backup and restore

Data is periodically copied to durable storage. After a disaster,
infrastructure is rebuilt from scratch and data is restored from the
most recent backup. Appropriate for non-critical workloads where
extended downtime is acceptable.

## Pilot light

A minimal environment runs in a secondary location — core data
replicated continuously, but compute resources stay dormant. On
failover, the dormant resources are scaled up. The "pilot light"
metaphor: a small flame kept burning so the furnace can ignite
quickly.

## Warm standby

A scaled-down but functional copy of the production environment runs
in the secondary location, continuously receiving replicated data.
Failover involves scaling up and redirecting traffic. The environment
is already running, so recovery is faster than pilot light but costs
more to maintain.

## Active-active

Full production capacity runs in multiple locations simultaneously,
with traffic distributed across them. A disaster in one location is
absorbed by the others. This requires the application to be designed
for multi-region operation — handling split-brain scenarios, conflict
resolution, and the consistency tradeoffs of distributed systems.

With synchronous replication, RPO approaches zero. With asynchronous,
RPO equals the replication lag.

## Related

- [RTO and RPO](rto-and-rpo.md) - The metrics these strategies target

---

Return to [SRE](_index.md)
