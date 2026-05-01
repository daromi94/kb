# Discovery service

The discovery service is the cluster's worker registry, embedded in the
coordinator and exposed over HTTP. It tracks which workers are alive and
where they are reachable. The scheduler consults it on every query to
decide where to place tasks.

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

| Field        | Purpose                                             |
|--------------|-----------------------------------------------------|
| Node UUID    | Stable identity for this JVM instance               |
| Internal URI | HTTP(S) address peers use for callbacks             |
| Node version | Trino build; mismatched versions are rejected       |
| Pool tags    | Resource pool membership                            |
| State        | ACTIVE, INACTIVE, or SHUTTING_DOWN (graceful drain) |

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

## Related

- [Architecture](architecture.md) - Where the coordinator fits in the cluster
- [Coordinator deep dive](coordinator-deep-dive.md) - Other coordinator subsystems
- [Fault-tolerant execution](fault-tolerant-execution.md) - The retry path on lost workers

---

Return to [Trino](_index.md)
