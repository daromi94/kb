# StatefulSets

StatefulSets manage applications that require stable, unique identities and
persistent storage. Unlike Deployments where Pods are interchangeable, a
StatefulSet Pod that dies is replaced with one having the same name, network
identity, and access to the same data.

## Core Guarantees

StatefulSets provide four guarantees that Deployments do not:

- **Stable network identifiers:** Pods are named with an ordinal index
  (`db-0`, `db-1`, `db-2`) that persists across rescheduling
- **Stable persistent storage:** Each Pod gets its own PersistentVolume; a
  restarted Pod re-attaches to its original disk
- **Ordered deployment:** Pods are created sequentially (0 to N-1); `db-1`
  won't start until `db-0` is Running and Ready
- **Ordered termination:** Scaling down terminates Pods in reverse order
  (N-1 to 0), ensuring data safety for distributed databases

## Headless Service Requirement

For stable network identity, a StatefulSet requires a Headless Service
(`clusterIP: None`). Instead of providing a single load-balanced IP, the DNS
system returns individual Pod IP addresses, enabling direct Pod-to-Pod
communication (e.g., follower connecting to leader for replication).

DNS format: `$(pod-name).$(service-name).$(namespace).svc.cluster.local`

## Volume Claim Templates

Deployments typically share a volume or use ephemeral storage. StatefulSets use
`volumeClaimTemplate` to create a unique PersistentVolumeClaim for each Pod,
ensuring `mariadb-0` and `mariadb-1` each have dedicated storage.

## When to Use

StatefulSets are appropriate for:

- **Distributed databases:** PostgreSQL, MySQL with replication, MongoDB,
  Cassandra
- **Cluster coordinators:** ZooKeeper, etcd (require quorum and node identity)
- **Message brokers:** Kafka, RabbitMQ (maintain ordering and persistent logs)

## StatefulSet vs Deployment

| Feature       | Deployment              | StatefulSet                    |
|---------------|-------------------------|--------------------------------|
| Pod naming    | Random (`web-a1b2c`)    | Ordinal (`web-0`, `web-1`)     |
| Storage       | Shared or ephemeral     | Dedicated per Pod              |
| Startup order | Parallel                | Sequential (0, 1, 2...)        |
| Network       | Single Service IP       | Individual Pod DNS (Headless)  |
| Use case      | Web APIs, microservices | Databases, distributed systems |

**Complexity warning:** StatefulSets are harder to manage than Deployments.
Strict ordering and persistent data make "stuck" updates common if a single Pod
fails its health check.

## Related

- [Deployments](deployments.md) - For stateless applications
