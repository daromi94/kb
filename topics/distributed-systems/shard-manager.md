# Shard Manager

## 1. The fundamental problem: distributing shards is not the same as distributing load

Shard Manager is a distributed control-plane system responsible for deciding **which application instance should own each shard**, monitoring the workload on those shards, and continuously adjusting placement to improve resource utilization.

**Shard placement should be driven by actual workload characteristics, not merely by hashing or shard counts.**

Consider a distributed service with six shards and three machines.

```text
Shard load
----------
Shard A              100
Shard B               80
Shard C               10
Shard D                5
Shard E                3
Shard F                2

Total load           200
```

A consistent-hashing scheme might distribute them as follows:

```text
     Host 1                Host 2                Host 3
+-------------+       +-------------+       +-------------+
| A: 100      |       | C:  10      |       | E:   3      |
| B:  80      |       | D:   5      |       | F:   2      |
+-------------+       +-------------+       +-------------+
   Load: 180             Load:  15             Load:   5

   OVERLOADED            UNDERUSED             UNDERUSED
```

Every host owns exactly two shards, but one host is handling 90% of the total workload.

This creates a serious capacity-planning problem.

Suppose an autoscaler detects the overloaded host and adds another machine. Consistent hashing redistributes some shards, but their selection is determined by the hash ring rather than their workload.

Consequently, adding machines does not necessarily relieve the hottest host.

This leads to a pathological feedback loop:

```text
      Uneven shard workload
                |
                v
   One host becomes overloaded
                |
                v
     Autoscaler adds capacity
                |
                v
Hashing redistributes some shards
                |
                v
 Hot shard may remain on hot host
                |
                v
Autoscaler adds even more capacity
                |
                v
     Many underutilized hosts
```

A decentralized hash-ring approach has two additional limitations.

**Decentralized ownership decisions.** Every application instance independently calculates ownership from its membership view. Because membership information propagates through gossip, different instances can temporarily disagree about which host owns a shard.

**Lack of operational control.** Operators cannot directly move a particular shard away from an overloaded machine. Instead, they must manipulate membership to influence placement.

Shard Manager addresses all three problems by introducing an explicit, load-aware ownership coordinator.

## 2. High-level architecture

The architecture separates two responsibilities:

- **Control plane:** Determines where shards should execute, manages ownership, detects failed hosts, and makes rebalancing decisions.
- **Data plane:** Executes the actual application workload and routes application requests directly to shard owners.

```text
                          CONTROL PLANE
+---------------------------------------------------------------+
|                                                               |
|                     SHARD MANAGER CLUSTER                     |
|                                                               |
|   +---------------+   +---------------+   +---------------+   |
|   | Manager A     |   | Manager B     |   | Manager C     |   |
|   |               |   |               |   |               |   |
|   | Leader (*)    |   | Replica       |   | Replica       |   |
|   +---------------+   +---------------+   +---------------+   |
|                                                               |
|   Responsibilities:                                           |
|   - Shard ownership                                           |
|   - Load-aware placement                                      |
|   - Failure detection                                         |
|   - Rebalancing                                               |
|   - Host/shard draining                                       |
+-------------------------------+-------------------------------+
                                |
                                | State / leader election
                                v
                     +----------------------+
                     | etcd                 |
                     |                      |
                     | Assignments          |
                     | Executor metadata    |
                     | Load statistics      |
                     | Drain state          |
                     +----------------------+


                        DATA PLANE

+----------------------+
| Frontend Service     |
|                      |
| Spectator client     |
| Cached shard map     |
+----------------------+
           |
           | Direct application requests
           |
           +---------------------------------+
           |                                 |
           v                                 v
+----------------------+          +----------------------+
| Executor A           |          | Executor B           |
|                      |          |                      |
| Shard 1              |          | Shard 3              |
| Shard 2              |          | Shard 4              |
|                      |          |                      |
| Application logic    |          | Application logic    |
+----------------------+          +----------------------+

Executors ------ heartbeats + load -----> Shard Manager

Shard Manager -- assignments -----------> Executors

Shard Manager -- streamed routing map --> Spectators
```

`(*)` Each namespace elects its own leader. Different namespaces can elect different managers.

**The request path never passes through Shard Manager.**

**Centralized placement decisions do not imply centralized request processing.**

### Main architectural components

| Component             | Responsibility                                                               |
| --------------------- | ---------------------------------------------------------------------------- |
| Shard Manager service | Ownership coordination, placement, rebalancing, liveness management          |
| Executor              | Runs the application logic associated with assigned shards                   |
| Spectator             | Discovers shard owners and routes requests to them                           |
| etcd                  | Durable coordination state, assignment persistence, leader election          |
| Namespace             | Isolates a shard population, its configuration, leader, and balancing policy |
| `smctl`               | Operational inspection, host draining, shard draining, and recovery controls |

## 3. Why separate executors from spectators?

A fundamental distinction in distributed sharded systems is that **the component that needs to locate work does not necessarily need to execute it.**

### Executors: processing shards

An executor is an application host responsible for processing its assigned shards.

The executor embeds a client library that handles communication with Shard Manager.

The lifecycle is roughly:

```text
       Executor starts
              |
              v
  Register / send heartbeat
              |
              v
  Receive shard assignments
              |
              v
    Start shard processors
              |
              v
   Execute application work
              |
              v
    Measure per-shard load
              |
              v
    Report load + liveness
              |
              v
 Receive updated assignments
              |
     +--------+--------+
     |                 |
     v                 v
 Start new        Stop removed
   shards            shards
```

The application integrates through a `ShardProcessor` interface exposing:

```text
ShardProcessor
    |
    +-- Start()
    |
    +-- Stop()
    |
    +-- GetShardReport()
    |
    +-- SetShardStatus()
```

Shard Manager understands that a shard has an owner, a load measurement, and a lifecycle. It does not need to understand the underlying application logic.

For example, a shard might represent a task queue, a state-machine partition, a stream-processing partition, or an in-memory index partition.

The application defines how its work begins, stops, and is measured. Shard Manager defines where that work should execute.

### Spectators: discovering owners

A spectator does not have to execute any shards. Its responsibility is to answer:

> Which executor currently owns shard X?

Spectators maintain a locally cached ownership map received through a gRPC stream.

For example:

```text
Spectator's cached routing table

+-----------+----------------+
| Shard     | Owner          |
+-----------+----------------+
| Task A    | Executor 1     |
| Task B    | Executor 3     |
| Task C    | Executor 2     |
+-----------+----------------+
```

A request for Task B is routed directly to Executor 3.

```text
       Client
         |
         v
Frontend / Spectator
         |
         | Local lookup: Task B -> Executor 3
         |
         v
     Executor 3
         |
         v
   Process Task B
```

This separation has four benefits:

1. Local lookups avoid a control-plane RPC for every application request.
2. Streaming updates avoid repeated polling for ownership changes.
3. The routing layer does not need direct access to etcd.
4. The control plane can become temporarily unavailable without necessarily interrupting requests to already-known healthy owners.

An application instance can act as both executor and spectator, allowing it to process its own shards while forwarding requests for other shards.

**Engineering lesson:** separate _ownership discovery_ from _ownership execution_. They have different performance characteristics and failure requirements.

## 4. Leadership, coordination, and etcd

A distributed shard manager must answer two different questions:

1. What is the current authoritative placement?
2. Which controller is allowed to change that placement?

The architecture uses etcd for both durable state and leader election.

### One leader per namespace

Shard Manager runs multiple service instances, but only one instance leads the rebalancing process for a particular namespace.

```text
                         Shard Manager instances

                    A               B               C
                    |               |               |
Namespace X       Leader         Follower        Follower
                    |
                    +---- Rebalance X


Namespace Y      Follower         Leader         Follower
                                    |
                                    +---- Rebalance Y


Namespace Z      Follower        Follower         Leader
                                                    |
                                                    +---- Rebalance Z
```

This avoids requiring every controller to independently compute and reconcile placement decisions.

It also allows different namespaces to have separate balancing configurations and leadership.

**Leadership is intentionally temporary.** In the default configuration, a leader holds its role for 60 seconds and then resigns so another manager can acquire leadership.

### The reconciliation loop

The leader operates as a reconciliation controller, much like a Kubernetes controller.

```text
  Observe cluster state <---------------------------+
            |                                       |
            v                                       |
   Find stale executors                             |
            |                                       |
            v                                       |
Collect unassigned shards                           |
            |                                       |
            v                                       |
 Evaluate load imbalance                            |
            |                                       |
            v                                       |
  Calculate shard moves                             |
            |                                       |
            v                                       |
      Commit to etcd                                |
            |                                       |
            v                                       |
   Publish assignments                              |
            |                                       |
            +-- Repeat -----------------------------+
```

The loop is triggered by a timer or an etcd watch notification when relevant state changes.

Each pass evaluates stale hosts, draining hosts, lost ownership, and possible load-balancing improvements, then commits the new assignment in a single etcd transaction.

The manager service also caches assignments and coalesces writes to reduce pressure on etcd.

```text
             Multiple controllers
                      |
                      v
Single placement decision-maker per namespace
                      |
                      v
        Transactional assignment state
                      |
                      v
Many independently executing application hosts
```

**Rationale:** serialize ownership decisions without serializing application execution.

### Why mediate etcd access through Shard Manager?

If executors and spectators accessed etcd directly, the application's client libraries would need to understand its persistence schema and coordination protocols.

By exposing gRPC APIs, Shard Manager hides those details.

```text
Applications
     |
     | Stable ownership API
     v
Shard Manager
     |
     | Internal storage adapter
     v
    etcd
```

The storage implementation can evolve independently of application integrations.

However, etcd introduces an operational and scalability cost.

The rebalance transaction compares the modification revision of every executor in a namespace. With etcd's default transaction operation limit of 128, this limits a namespace to approximately 128 executors.

**The coordination layer's transaction limits can constrain horizontal scalability even when the application data plane scales independently.**

## 5. Load-aware balancing: the core algorithm

The placement algorithm balances executor load while limiting shard movement.

A traditional hash ring can produce deterministic assignments with little coordination. Shard Manager instead maintains explicit assignments and continuously optimizes them.

The objective is not simply:

```text
Minimize maximum host load
```

It is closer to:

```text
Minimize imbalance subject to acceptable movement
```

Because moving shards has a cost.

### Greedy balancing

The greedy algorithm periodically computes the aggregate load of every executor from the reported loads of its shards.

Suppose two hosts have:

```text
         Host A                          Host B
+----------------------+        +----------------------+
| Shard 1: 100         |        | Shard 3: 40          |
| Shard 2:  60         |        |                      |
+----------------------+        +----------------------+
       Total: 160                      Total: 40

                      Average: 100
```

The naive solution might move the largest shard.

```text
Move Shard 1 (100)

Host A = 60
Host B = 140
```

That remains imbalanced.

The better solution moves Shard 2.

```text
Move Shard 2 (60)

Host A = 100
Host B = 100
```

The greedy algorithm evaluates candidate shard moves between overloaded and underloaded executors, seeking the move that most improves their balance.

This is not a full global optimization problem solved every time. It is a relatively cheap heuristic designed for continuous operation.

### Why not rebalance continuously?

Imagine a shard oscillating between high and low traffic.

```text
Time        T1       T2       T3       T4       T5
Load        100      130       95      140      100
```

If every short-lived spike triggers an ownership transfer, the system can spend substantial resources migrating shards.

Worse, transfers can create additional workload that then triggers more balancing.

Shard Manager applies four controls.

| Mechanism          | Purpose                                                     |
| ------------------ | ----------------------------------------------------------- |
| Load smoothing     | Avoid reacting to transient variations                      |
| Hysteresis         | Avoid rebalancing hosts already close enough to the average |
| Movement budget    | Limit the number of moves in one reconciliation pass        |
| Per-shard cooldown | Avoid repeatedly moving the same shard                      |

The greedy balancer's defaults include a one-minute load-smoothing time constant, a one-minute movement cooldown, a 1% shard-move budget per pass, and upper/lower load thresholds of 115% and 90% of average load.

### Hysteresis

Consider a cluster with average host load of 100.

```text
Acceptable region

Too cold            Acceptable                  Too hot
Load < 90           90 <= Load <= 115           Load > 115

Average load = 100
```

A host above 115 becomes a candidate source for moves.

A host below 90 becomes a candidate destination.

Hosts in the acceptable region are generally left unchanged.

This is not perfectly equal distribution, and that is deliberate.

Perfect balancing may require continuous migrations whose costs exceed their benefits.

### Movement budget

If a namespace contains 1,000 assigned shards, the default 1% movement budget permits up to 10 greedy load-based moves per pass.

```text
       Current placement
               |
               v
    Select beneficial moves
               |
               v
       Apply <= 10 moves
               |
               v
Observe subsequent load reports
               |
               v
        Reconcile again
```

This trades convergence speed for stability. There is also an exception allowing more flexible destination selection under severe imbalance.

**Engineering lesson:** optimization in a dynamic distributed system should minimize not only steady-state cost, but also the disruption caused by changing the system.

A mathematically better placement can be operationally worse if achieving it requires expensive, frequent movement.

## 6. Failure recovery and ownership transitions

Ownership coordination becomes especially important when executors fail.

### Executor failure

Each executor periodically sends heartbeats containing liveness information, metadata, and shard status.

The manager detects executors whose heartbeats have exceeded a configured TTL.

```text
                  Normal operation

Executor A                           Shard Manager
    |                                      |
    | -------- Heartbeat ----------------> |
    | <------- Assignments --------------- |
    |                                      |
    | -------- Heartbeat ----------------> |
    |                                      |
    X  Process crashes                     |
                                           |
                                   Heartbeat expires
                                           |
                                   Mark A as stale
                                           |
                                   Reassign A's shards
                                           |
                                           v
                                       Executor B
```

This supports automatic recovery when a host disappears.

However, failure detection is based on heartbeat timeouts, and distributed systems cannot always distinguish a crashed host from one that is merely delayed or partitioned.

**A host might still be processing work when the controller considers it stale.**

**This is why an authoritative assignment record is not, by itself, a complete exactly-once execution guarantee.**

For workloads requiring strict single-writer safety, additional mechanisms may be necessary, such as fencing tokens, transactional ownership checks, or resource-specific leases.

### Host draining versus shard draining

These are distinct operational capabilities.

**Host draining** reassigns all shards away from a particular executor and prevents further assignments to it. It is useful for deployments, maintenance, and degraded hosts.

**Shard draining** prevents a specific shard from being assigned at all.

Suppose one malformed shard repeatedly causes the executor handling it to crash.

Without shard-level isolation:

```text
     Bad shard
         |
         v
   Crashes Host A
         |
         v
Reassigned to Host B
         |
         v
   Crashes Host B
         |
         v
Reassigned to Host C
         |
         v
   Crashes Host C
```

Automatic recovery becomes a cascading-failure mechanism.

With shard draining:

```text
  Bad shard detected
          |
          v
Mark shard as drained
          |
          v
   Stop assignment
          |
          v
 Investigate / repair
          |
          v
    Restore shard
```

**Engineering lesson:** recovery mechanisms must distinguish between faulty infrastructure and faulty work.

**Moving a poisoned workload is not recovery. It can propagate the failure.**

Shard draining provides targeted load shedding and blast-radius containment.

## 7. Fixed versus ephemeral shards

Shard Manager supports two different shard lifecycles.

|                   | Fixed shards                     | Ephemeral shards              |
| ----------------- | -------------------------------- | ----------------------------- |
| Creation          | Predefined shard population      | Created on demand             |
| Lifetime          | Persist as part of the namespace | Retired when finished or idle |
| Intended workload | Stable partitions                | Dynamic application work      |
| Example           | Workflow history partitions      | On-demand jobs                |

For fixed shards, the system knows the total shard count in advance and attempts to maintain their assignments.

For ephemeral shards, a lookup can cause a shard to be created. The executor reports its status, and a shard marked `DONE` leaves the active population.

This avoids requiring every possible dynamically generated shard key to exist permanently.

The distinction matters because a scheduling system processing millions of short-lived tasks behaves differently from a storage system managing a fixed partition population.

## 8. Placement trade-offs

**Decentralized ownership**

Hashing is simple, and each instance can derive placement independently. But membership disagreement complicates correctness and load-based steering.

**Centralized ownership**

Explicit, inspectable placement enables precise balancing and draining, at the expense of an additional coordination dependency.

**Aggressive balancing**

Converges quickly after workload changes but creates more ownership transitions and potentially more disruption.

**Conservative balancing**

Uses smoothing, hysteresis, and cooldowns to avoid churn, but leaves imbalance unresolved longer.

**Stateless processing shards**

Cheap to move; suitable for frequent load balancing.

**Stateful processing shards**

Can require checkpointing, transfer, cache warming, and fencing. A good placement may be expensive to reach.

**The correct placement policy depends on the cost of moving the workload.**

A general cost model for stateful shard placement adds a migration penalty to the load imbalance cost.

```text
Total cost = Load imbalance cost + lambda * Migration cost
```

In this model, `lambda` controls how strongly migration cost affects placement decisions. Shard Manager limits movement through its greedy heuristic and movement controls.

## 9. Engineering principles

**First: separate logical ownership from physical placement.**

Shard identities should remain stable even when their physical executors change. A dedicated ownership layer makes movement an explicit, manageable operation.

**Second: treat coordination state as operationally valuable.**

An inspectable source of truth makes it possible to answer questions like which host owns a shard, why it was moved, and which work has been drained.

**Third: keep the coordination system out of the hot path.**

The control plane may require consensus, persistence, and periodic reconciliation. Request execution should not incur those costs on every operation.

**Fourth: optimize for resource demand, not item count.**

Equal numbers of partitions, tasks, or tenants do not imply equal CPU, memory, bandwidth, or I/O demand. The load signal must reflect the resource being optimized.

**Fifth: reconfiguration is an operation with a cost.**

A good scheduler needs stability controls, not just an effective placement heuristic. For stateful workloads, migration mechanisms can become as important as the placement algorithm.

**Sixth: distinguish failure recovery from failure propagation.**

Reassigning every failed shard indefinitely can create cascading failures. Selective shard isolation is an essential operational capability.

**Seventh: observe scalability limits in the control plane separately from those in the data plane.**

A fleet might have ample compute capacity but be limited by coordination transaction sizes, watch fan-out, heartbeat throughput, or leader reconciliation capacity.

### Placement and execution

Shard Manager represents a shift from _implicit, membership-derived ownership_ to _explicit, workload-driven ownership_.

```text
Traditional consistent hashing

       Cluster membership
               |
               v
         Hash function
               |
               v
        Shard placement

Explicit shard management

       Cluster membership
               +
      Observed shard loads
               +
    Operational constraints
               +
      Existing assignments
               |
               v
      Placement controller <-----------------------+
               |                                   |
               v                                   |
    Authoritative ownership                        |
               |                                   |
               v                                   |
     Application execution                         |
               |                                   |
               v                                   |
         Load feedback                             |
               |                                   |
               +-- Controller ---------------------+
```

**Placement and execution are different problems.**

Execution needs a fast, scalable data plane. Placement needs a coordinated, observable control plane capable of adapting to workload changes without creating excessive disruption.

Separating placement from execution allows resource utilization, failure isolation, and placement policies to evolve independently of the underlying application.
