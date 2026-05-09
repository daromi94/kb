# Architecture

DynamoDB is composed of tens of microservices. Four core services
handle the request path and system management.

## Request path

```text
Client
  |
  v
+-----------------+      +--------------------+
| Request router  |----->| Metadata service   |
| (auth, routing) |<-----| (table->partition) |
+-----------------+      +--------------------+
  |
  | route to partition leader
  v
+----------------+
| Storage node   |
| (multi-tenant) |
+----------------+
```

**Request router** is the entry point for all API calls. It
authenticates and authorizes every request, then consults the
metadata service to locate the target partition. Data operations
route directly to the appropriate storage node.

**Metadata service** maps tables and indexes to the replication
groups that hold their data. Request routers cache this mapping
locally via MemDS, a distributed in-memory store that avoids
bimodal cache behavior.

**Storage nodes** physically store customer data. Each node is
multi-tenant — it hosts replicas from many partitions belonging
to different tables.

## Autoadmin service

The autoadmin service is the control plane. It operates
autonomously without human intervention.

| Responsibility      | Behavior                                               |
|---------------------|--------------------------------------------------------|
| Fleet health        | Monitors every partition and component for degradation |
| Automated recovery  | Replaces unhealthy replicas to restore quorum          |
| Resource management | Handles table creation, schema changes, and scaling    |

When a storage node or replica is unhealthy — bad hardware, high
latency — autoadmin triggers recovery to replace affected replicas
and restore the replication group to full strength.

---

Return to [DynamoDB](_index.md)
