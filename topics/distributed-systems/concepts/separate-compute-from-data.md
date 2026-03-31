# Separate compute from data

Decoupling compute and storage into independent layers allows each to scale
according to its own demand rather than scaling together as a monolithic unit.

## The architectural split

**Compute layer:** Stateless nodes or containers that execute logic, run
queries, and perform transformations. They do not own data and can be spun
up or shut down based on demand.

**Storage layer:** A persistent, highly available service (S3, Azure Blob
Storage, or a distributed file system) responsible for durability and
accessibility.

```text
+-------------------+     +-------------------+
|  Compute Node A   |     |  Compute Node B   |
|   (stateless)     |     |   (stateless)     |
+---------+---------+     +---------+---------+
          |                         |
          |       fetch / push      |
          v                         v
+-------------------------------------------+
|            Storage Layer                  |
|         (stateful, durable)               |
+-------------------------------------------+
```

## Benefits

**Independent scaling.** A retail system during a sale may need 10x compute
for checkout logic while the dataset size stays constant. Scale compute to
100 nodes while storage remains unchanged.

**Cost efficiency.** Use cheap, high-capacity hardware for storage and
high-performance instances for compute. Pay for expensive compute only when
it is actively working.

**Resiliency.** If a compute node crashes, no data is lost. Route the
request to a new node that fetches the required state from storage.

## The network latency trade-off

In a shared-nothing architecture, the CPU talks to a local disk. In a
separated architecture, the CPU fetches data over the network. Systems
mitigate this with:

- **Heavy caching** — Compute nodes keep a hot copy of data locally
- **High-bandwidth networking** — 100 Gbps links make the network approach
  local bus speeds
- **Metadata services** — A separate service tracks where data lives in the
  storage layer so compute nodes avoid searching for it

## Related

- [Stateless vs stateful](stateless-vs-stateful.md) - Compute layer is
  stateless, storage layer is stateful
- [Control plane vs data plane](control-plane-data-plane.md) - Similar
  separation of concerns between management and request processing

---

Return to [Concepts](_index.md)
