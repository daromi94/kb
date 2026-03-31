# Control plane vs data plane

The separation of control planes and data planes isolates concerns, optimizes
performance, and enhances system resilience.

## Definitions

**Data plane (forwarding plane):** The critical path of request processing.
Moves and transforms data based on configuration the control plane provides.

- Latency-sensitive, high throughput
- Scales linearly with request volume — O(requests)
- Must maintain near-constant uptime; failure directly impacts users

**Control plane (management plane):** Operates out-of-band from the request
path. Manages system metadata, configuration orchestration, and global state
coordination.

- Consistency-oriented
- Scales with managed nodes or entities — O(nodes)
- Prioritizes strong consistency (CP in CAP) over high availability
- Handles complex logic (leader election, sharding) asynchronously

```text
+-------------------+
|   Control Plane   |
|   (consistency)   |
|        |          |
|        | config   |
|        v          |
+-------------------+
|    Data Plane     |
|   (performance)   |
+-------------------+
         |
         v
      requests
```

## Architectural challenges

### Hard dependencies and availability

System availability is bounded by the least available hard dependency. If the
data plane requires synchronous calls to the control plane:

$$\alpha_{sys} = \alpha_{data} \times \alpha_{control}$$

Mitigation: **Static stability**. The data plane must continue operating with
cached or stale state when the control plane becomes unreachable.

### Scale disparity and thundering herds

The planes scale at different magnitudes. When massive data plane restarts
occur, a thundering herd of configuration requests can overwhelm the control
plane.

## Mitigation strategies

| Strategy               | Mechanism                                                                   |
|------------------------|-----------------------------------------------------------------------------|
| Blob storage buffer    | Control plane persists state to object store (S3); data plane polls it      |
| Push-based propagation | Control plane pushes deltas via long-lived connections with back-pressure   |
| Hybrid snapshotting    | New nodes bootstrap from storage snapshot, then subscribe for delta updates |

## Complexity isolation

Separating planes allows specialized algorithms for each concern:

| Plane   | Optimized for | Example algorithm |
|---------|---------------|-------------------|
| Data    | Performance   | Chain replication |
| Control | Correctness   | Paxos/Raft        |

This prevents the performance-critical path from being bogged down by
distributed consensus overhead.

## Recursive and heterogeneous patterns

In large-scale systems, the pattern becomes recursive:

- **Meta-control planes:** A control plane managing many data planes may need
  its own control plane for scaling and deployment
- **Specialized control planes:** A single system may have separate control
  planes for fault tolerance (low latency), autoscaling (metric-driven), and
  provisioning (customer-facing CRUD)

## Related

- [Separate compute from data](separate-compute-from-data.md) - Similar
  separation between processing and storage layers
- [Stateless vs stateful](stateless-vs-stateful.md) - Data plane is often
  stateless, control plane is stateful

---

Return to [Concepts](_index.md)
