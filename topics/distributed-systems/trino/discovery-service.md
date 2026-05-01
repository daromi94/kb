# Discovery service

The discovery service is the cluster's worker registry, embedded in the
coordinator and exposed over HTTP. It tracks which workers are alive and
where they are reachable. The scheduler consults it on every query to
decide where to place tasks.

The registry has no external dependency — no ZooKeeper, no etcd, no
consensus protocol. It is a single in-memory map on the coordinator.

## Heartbeat mechanism

Workers push periodic HTTP heartbeats to the coordinator. There are no
long-lived TCP or WebSocket sessions to maintain.

### Worker announcement

On startup, a worker reads the coordinator's discovery URI from its config
and generates a node UUID that lives for the JVM's lifetime. A background
thread then PUTs heartbeats to the coordinator's announcement endpoint
(`/v1/announcement`).

### Heartbeat payload

Each heartbeat carries the metadata the scheduler needs:

| Field        | Purpose                                              |
|--------------|------------------------------------------------------|
| Node UUID    | Stable identity for this JVM instance                |
| Internal URI | HTTP(S) address other nodes use to reach this worker |
| Node version | Trino build; mismatched versions are rejected        |
| Pool tags    | Resource pool membership                             |
| State        | ACTIVE, INACTIVE, or SHUTTING_DOWN (graceful drain)  |

Version matching keeps mismatched workers out during a rolling upgrade —
they cannot accept tasks until their build matches the coordinator's.

## Leases and eviction

The discovery service holds an in-memory ledger of announced nodes, each
with a `last-seen` timestamp.

- **Renewal:** Every valid heartbeat updates `last-seen`, refreshing the
  lease.
- **Reaper:** A background task scans the ledger and compares each
  `last-seen` against the maximum age threshold. Any node that misses
  the window — typically from a JVM GC pause, a hardware fault, or a
  network partition — is removed from the registry.

Eviction is final: a removed worker must re-announce itself before it is
considered for scheduling again.

### Active failure detection

Alongside TTL-based eviction, the coordinator probes each known worker
over HTTP and tracks success rates over a rolling window. A worker
failing too many probes is dropped from the active set even if it is
still announcing itself. This catches workers whose announcement thread
runs while the rest of the JVM is unresponsive — typically a GC
death-spiral.

## Node states

The coordinator classifies every known node into one of four states:

| State         | Meaning                                              |
|---------------|------------------------------------------------------|
| Active        | Recently announced and reachable                     |
| Missing       | Active but momentarily silent; TTL has not expired   |
| Inactive      | TTL expired or failure detector marked the node dead |
| Shutting down | Worker reported SHUTTING_DOWN via `/v1/info/state`   |

The scheduler only places splits on Active nodes. Shutting-down workers
finish in-flight tasks and exit; the coordinator stops sending them new
work as soon as it sees the state change.

## Integration with scheduling

The execution layer reads the registry through the NodeManager, which
exposes a snapshot of the currently active workers.

### Task placement

When the NodeScheduler distributes a PlanFragment, it asks the NodeManager
for the active set and assigns tasks and splits only to those workers.

### Mid-query failure

If a worker's lease expires while it has running tasks, the coordinator's
response depends on the execution mode:

| Mode           | Behavior on lost worker                                   |
|----------------|-----------------------------------------------------------|
| Default        | Abort the query; client gets a node-failure error         |
| Fault-tolerant | Mark the failed task, find a healthy replacement, restart |

In default mode, in-flight work on the dead worker is unrecoverable — its
intermediate state lived only in that worker's memory.

## Tradeoffs

The single-coordinator, in-memory design suits an analytics workload:

- **No external dependency:** Nothing else to run alongside the cluster.
- **No new failure mode:** The coordinator is a single point of failure
  for membership, but it is already the single point of failure for
  query planning.
- **Eventually consistent:** A new worker takes seconds to become
  schedulable; a dead worker takes up to ~30s to fall out. Fine when
  queries last seconds to minutes; too slow for a low-latency RPC mesh.
- **Stateless:** A coordinator restart wipes the registry, but workers
  re-announce within seconds and the cluster reconverges.

Multi-coordinator high availability requires a routing gateway: each
coordinator runs its own registry against its own pool of workers, and
clients reach the gateway rather than any individual coordinator. The
discovery layer itself is never clustered.

## Related

- [Architecture](architecture.md) - Where the coordinator fits in the cluster
- [Coordinator deep dive](coordinator-deep-dive.md) - Other coordinator subsystems
- [Fault-tolerant execution](fault-tolerant-execution.md) - The retry path on lost workers

---

Return to [Trino](_index.md)
