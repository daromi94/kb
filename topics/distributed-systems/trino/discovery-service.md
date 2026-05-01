# Discovery service

The discovery service is the cluster's worker registry, embedded in the
coordinator and exposed over HTTP. It tracks which workers are alive and
where they are reachable, and the scheduler reads its state on every query
to decide where to place tasks.

## Heartbeat mechanism

Health monitoring is poll-based, not connection-based. Workers periodically
push their state to the coordinator over HTTP — there are no long-lived
TCP or WebSocket sessions to keep alive.

### Worker announcement

On startup, a worker reads the coordinator's discovery URI from its config
and generates a node UUID that lives for the JVM process lifetime. It then
spins up a background thread that PUTs heartbeats to the coordinator's
announcement endpoint (`/v1/announcement`).

### Heartbeat payload

Each heartbeat carries metadata the scheduler needs:

| Field        | Purpose                                                |
|--------------|--------------------------------------------------------|
| Node UUID    | Stable identity for this JVM instance                  |
| Internal URI | HTTP(S) address peers and the coordinator dial back on |
| Node version | Trino build; mismatched versions are rejected          |
| Pool tags    | Resource pool membership                               |
| State        | ACTIVE, INACTIVE, or SHUTTING_DOWN (graceful drain)    |

Version matching keeps a partially upgraded cluster from running
heterogeneous binaries against the same query.

## Leases and eviction

The discovery service holds an in-memory ledger of announced nodes, each
with a `last-seen` timestamp.

- **Renewal:** Every valid heartbeat updates `last-seen`, refreshing the
  lease.
- **Reaper:** A background scan compares `last-seen` against the maximum
  age threshold. Any node that has not heartbeated within the window —
  typically because of a JVM GC pause, a hardware fault, or a network
  partition — is removed from the registry.

Eviction is final: a removed worker must re-announce itself before it is
considered for scheduling again.

## Integration with scheduling

The execution layer reads the registry through the NodeManager, which
exposes a snapshot of the active set.

### Task placement

When the NodeScheduler distributes a PlanFragment, it asks the NodeManager
for the current active nodes and assigns tasks and splits only to that
snapshot.

### Mid-query failure

If a worker's lease expires while it has running tasks, the coordinator
reacts based on execution mode:

| Mode           | Behavior on lost worker                                   |
|----------------|-----------------------------------------------------------|
| Default        | Abort the query; client gets a node-failure error         |
| Fault-tolerant | Mark the failed task, find a healthy replacement, restart |

In default mode, anything in flight on the dead worker is unrecoverable
because intermediate state lives only in its memory.

## Related

- [Architecture](architecture.md) - Where the coordinator fits in the cluster
- [Coordinator deep dive](coordinator-deep-dive.md) - Other coordinator subsystems
- [Fault-tolerant execution](fault-tolerant-execution.md) - The retry path on lost workers

---

Return to [Trino](_index.md)
