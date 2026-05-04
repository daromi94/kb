# Death watch

Death watch is an asynchronous notification mechanism that lets any
actor monitor any other actor's termination. Unlike supervision,
which is restricted to parent-child relationships, death watch works
across the entire hierarchy — siblings, parents, or remote actors in
a cluster.

## Properties

- **Unidirectional.** If A watches B, B does not automatically
  watch A.
- **Observation only.** The watcher receives a notification but
  cannot force a restart — that power belongs to the supervisor.

## Protocol

An actor subscribes by calling `context.watch(targetRef)`. When the
target stops, the watcher receives a Terminated signal:

```scala
Behaviors.receiveSignal {
  case (context, Terminated(ref)) =>
    context.log.info("Actor {} terminated", ref.path)
    Behaviors.stopped
}
```

If the watcher does not handle the Terminated signal, a
DeathPactException is thrown — stopping the watcher itself.

## Death watch vs supervision

| Aspect       | Supervision          | Death watch                   |
|--------------|----------------------|-------------------------------|
| Relationship | Parent-child only    | Any actor to any actor        |
| Purpose      | Fault recovery       | Lifecycle and dependency mgmt |
| Trigger      | Unhandled exception  | Termination or node failure   |
| Control      | Decides child's fate | Observes only                 |

## Use cases

**Dependency management.** An actor that relies on a service actor
should watch it. If the service terminates, the dependent actor can
stop or transition to a waiting state rather than sending messages
that will never arrive.

**Cluster monitoring.** Remote death watch uses heartbeats and a
failure detector to generate Terminated signals from network
failures and JVM crashes, not just graceful stops.

**Orderly shutdown.** A parent watches its children to detect when
all work is complete before shutting itself down.

## Related

- [Supervision](supervision.md) - Parent-child fault handling
- [Hierarchical design](hierarchical-design.md) - Hierarchy design guidelines
- [Guardian actors](guardian-actors.md) - Top-level guardians and shutdown

---

Return to [Pekko](_index.md)
