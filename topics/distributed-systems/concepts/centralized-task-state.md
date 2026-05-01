# Centralized task state

In distributed task execution — query engines, job schedulers,
workflow systems — one node (the coordinator) owns the
authoritative state machine for every task. Workers receive the
work, execute it, and report progress, but they never decide what
state a task is in. The coordinator does.

## States

A typical task moves through:

```text
PLANNED -> RUNNING -> {DONE | FAILED | CANCELED}
```

The terminal states (DONE, FAILED, CANCELED) are absorbing. Once
the coordinator transitions a task into a terminal state, no later
event moves it back. Stale or out-of-order worker reports are
dropped, not applied.

## Why centralize state

| Concern             | Centralized                  | Peer-to-peer              |
|---------------------|------------------------------|---------------------------|
| Source of truth     | One node                     | All nodes                 |
| Cancel propagation  | One sender, fan-out          | All-to-all gossip         |
| Failure correlation | Coordinator picks root cause | Each node decides locally |
| Topology knowledge  | Coordinator only             | Every worker              |

Workers gossiping state requires every worker to know the full DAG
topology and produces $O(n^2)$ messaging during failures.
Centralizing gives $O(n)$ failure broadcast and lets the
coordinator de-duplicate and correlate worker reports into a single
decision.

## Pushed, not pulled

Cancellation needs to travel fast, so the coordinator pushes state
transitions through the control plane — long-lived RPC streams,
long-poll, or persistent connections. Polling means workers wait up
to one polling interval to see a cancel; at sub-second timescales
that is an entire task's budget.

## Failure as state transition

A worker failure becomes a coordinator-owned transition:

1. Worker reports the failure to the coordinator.
2. Coordinator marks the task FAILED.
3. Coordinator pushes CANCELED to every sibling task.

Failure propagation reduces to two coordinator decisions, not a
broadcast storm among workers.

## The single point of failure

Centralization makes the coordinator critical. Coordinator failure
strands every running task. Most systems accept this and require
the client to retry; investing in coordinator high availability
requires replicating the state machine itself.

## Related

- [Control plane vs data plane](control-plane-data-plane.md) - The
  coordinator drives the control plane; workers exchange data
  out-of-band on the data plane
- [Leader and followers](leader-and-followers.md) - Similar
  centralization for durable replicated state rather than ephemeral
  task lifecycle
- [Heartbeat](heartbeat.md) - Liveness signal that detects
  unresponsive workers

---

Return to [Concepts](_index.md)
