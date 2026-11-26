# Orchestration vs. choreography

Orchestration and choreography are two architectural patterns for coordinating distributed components to accomplish a common objective.

The fundamental distinction is **where coordination logic lives and who owns the responsibility for progressing a workflow**.

- **Orchestration:** Coordination is explicitly managed by a logical controller.
- **Choreography:** Coordination emerges from interactions between autonomous participants.

Both distribute execution across multiple components, but they distribute decision-making differently.

## 1. The coordination problem

Consider a distributed system composed of several independent services:

```text
+-----------+   +-----------+   +-----------+
| Payment   |   | Inventory |   | Shipping  |
+-----------+   +-----------+   +-----------+
```

Each service implements a specific capability. However, fulfilling an order requires coordinating these capabilities into a larger operation.

```text
 Charge payment
        |
        v
Reserve inventory
        |
        v
 Create shipment
```

This introduces a set of coordination problems:

- How are dependencies between operations enforced?
- Who determines which operation executes next?
- Who tracks the progress of the workflow?
- What happens when an operation fails?
- Who determines whether the overall operation has succeeded?

Orchestration and choreography provide different answers to these questions.

## 2. Orchestration

Orchestration introduces a dedicated logical component responsible for coordinating the execution of a workflow.

```text
             +----------------+
             | Orchestrator   |
             +----------------+
                      |
      +---------------+---------------+
      |               |               |
      v               v               v
+-----------+   +-----------+   +-----------+
| Payment   |   | Inventory |   | Shipping  |
+-----------+   +-----------+   +-----------+
```

The orchestrator contains the business logic that describes how individual operations must be composed.

Conceptually:

```text
FUNCTION fulfill_order(order):
    charge_payment(order)
    reserve_inventory(order)
    create_shipment(order)
    complete_order(order)
```

The participating services implement individual capabilities without necessarily knowing how those capabilities fit into the larger workflow.

### Execution model

```text
Orchestrator        Payment        Inventory       Shipping
      |                |               |               |
      |-- Charge ----->|               |               |
      |<-- Success ----|               |               |
      |                |               |               |
      |-- Reserve -------------------->|               |
      |<-- Success --------------------|               |
      |                |               |               |
      |-- Ship --------------------------------------->|
      |<-- Success ------------------------------------|
      |                |               |               |
  Completed
```

**The orchestrator explicitly determines what happens next based on the results of previous operations.**

### Workflow ownership

The workflow becomes an independently managed entity, potentially with its own durable state, identity, lifecycle, and execution policies.

```text
Workflow ID: order-123

+--------------------+-----------+
| Operation          | State     |
+--------------------+-----------+
| Charge payment     | COMPLETED |
| Reserve inventory  | COMPLETED |
| Create shipment    | RUNNING   |
| Complete order     | PENDING   |
+--------------------+-----------+
```

A durable orchestrator can persist this information and recover execution after failures.

The orchestrator can also implement scheduling, retries, deadlines, cancellation, dependency resolution, compensation, concurrency limits, and admission control.

### Separation of coordination and execution

One of the most important architectural properties of orchestration is the separation of **what should happen** from **how it happens**.

```text
+-------------------------------+
| Coordination Layer            |
|                               |
| Workflow state                |
| Dependency management         |
| Scheduling                    |
| Failure handling              |
+-------------------------------+
                |
                | Commands / Status
                |
+-------------------------------+
| Execution Layer               |
|                               |
| Workers                       |
| Computation                   |
| Storage operations            |
| Network operations            |
+-------------------------------+
```

This resembles the control plane and data plane separation commonly found in distributed infrastructure.

The orchestrator can understand the logical structure of an operation without participating directly in its computationally expensive execution.

## 3. Choreography

Choreography distributes coordination logic among the participating components.

Rather than receiving instructions from a central coordinator, components independently react to events and produce new events.

```text
+-----------+   +-----------+   +-----------+
| Payment   |   | Inventory |   | Shipping  |
+-----------+   +-----------+   +-----------+
      |               |               |
      v               v               v
+-------------------------------------------+
| Event Broker                              |
+-------------------------------------------+
```

The event broker provides communication infrastructure but does not necessarily understand or manage the business workflow.

### Execution model

```text
     OrderCreated
           |
           v
+---------------------+
| Payment Service     |
+---------------------+
           |
           v
   PaymentCompleted
           |
           v
+---------------------+
| Inventory Service   |
+---------------------+
           |
           v
   InventoryReserved
           |
           v
+---------------------+
| Shipping Service    |
+---------------------+
           |
           v
     OrderShipped
```

Each participant defines its own behavior.

```text
Payment Service:

    ON OrderCreated:
        charge_payment()
        publish PaymentCompleted
```

```text
Inventory Service:

    ON PaymentCompleted:
        reserve_inventory()
        publish InventoryReserved
```

```text
Shipping Service:

    ON InventoryReserved:
        create_shipment()
        publish OrderShipped
```

No dedicated component needs to explicitly instruct each service to execute its operation.

**The global behavior emerges from the composition of local behaviors.**

### Distributed workflow state

Unlike orchestration, the state of the workflow is often distributed across participants.

```text
+-----------------------+
| Payment Database      |
| order-123: PAID       |
+-----------------------+

+-----------------------+
| Inventory Database    |
| order-123: RESERVED   |
+-----------------------+

+-----------------------+
| Shipping Database     |
| order-123: PROCESSING |
+-----------------------+
```

Determining the overall state may require correlating events, querying multiple services, or maintaining a materialized view of workflow progress.

**An individual service can know its local state without knowing the global state.**

## 4. Commands vs. events

The distinction between commands and events is useful for understanding both patterns.

A **command** expresses an intention.

```text
ReserveInventory
ChargePayment
CreateShipment
```

An **event** describes something that has already happened.

```text
InventoryReserved
PaymentCompleted
ShipmentCreated
```

| Property        | Command              | Event                         |
| --------------- | -------------------- | ----------------------------- |
| Meaning         | Perform an operation | Something happened            |
| Semantics       | Imperative           | Declarative fact              |
| Recipient       | Usually specific     | Potentially multiple          |
| Responsibility  | Requests an action   | Consumers decide how to react |
| Typical pattern | Orchestration        | Choreography                  |

In orchestration:

```text
Orchestrator -- ReserveInventory --> Inventory
```

In choreography:

```text
Payment -- PaymentCompleted --> Event Broker
                                      |
                         +------------+--------------+
                         |            |              |
                         v            v              v
                     Inventory    Analytics      Auditing
```

The producer of an event does not necessarily know which consumers exist or what they will do.

However, this distinction is not absolute. An orchestrator can consume events and issue asynchronous commands. Choreography can also involve direct service interactions.

**The communication mechanism does not determine the coordination model. The ownership of coordination logic does.**

## 5. Coupling

Choreography is frequently described as loosely coupled, while orchestration is described as tightly coupled. This is an oversimplification.

Both introduce coupling, but in different places.

### Orchestration: centralized workflow coupling

```text
             Orchestrator
                   |
   +---------------+---------------+
   |               |               |
Payment        Inventory       Shipping
```

The orchestrator is coupled to the capabilities and contracts of the participating services.

However, the participants do not necessarily depend on one another.

Changing the order of execution can potentially be accomplished by modifying only the orchestrator.

### Choreography: distributed behavioral coupling

```text
Payment --> Inventory --> Shipping
```

Services may not depend on each other's network addresses or availability, but their behavior depends on the events produced by other participants.

For example, inventory reservation depends on the semantic meaning of `PaymentCompleted`.

This creates **semantic coupling** and **implicit workflow dependencies**.

| Type of coupling      | Orchestration             | Choreography                    |
| --------------------- | ------------------------- | ------------------------------- |
| Workflow coupling     | Concentrated              | Distributed                     |
| Temporal coupling     | Depends on implementation | Often reduced through messaging |
| Semantic coupling     | Service contracts         | Event contracts                 |
| Participant awareness | Generally lower           | Depends on event design         |
| Workflow evolution    | Often localized           | Potentially cross-service       |

An event broker can eliminate direct communication dependencies without eliminating business dependencies.

## 6. Failure handling

Failure handling is one of the areas where the differences become particularly important.

Consider the following situation:

```text
      Payment completed
              |
              v
Inventory reservation failed
              |
              v
What happens to the payment?
```

The system must compensate for the completed payment.

### Orchestration

The orchestrator explicitly manages the failure and determines the corrective action.

```text
           +--------------+
           | Orchestrator |
           +--------------+
                   |
      +------------+------------+
      |                         |
   Charge                    Reserve
      |                         |
      v                         v
+-----------+             +-----------+
| Payment   |             | Inventory |
+-----------+             +-----------+
      |                         |
   SUCCESS                   FAILURE
      |                         |
      +------------+------------+
                   |
                   v
             Orchestrator
                   |
                   | RefundPayment
                   v
                Payment
```

Conceptually:

```text
FUNCTION fulfill_order(order):
    charge_payment(order)

    IF NOT reserve_inventory(order):
        refund_payment(order)
        fail_order(order)
        RETURN

    create_shipment(order)
```

Compensation policies are explicitly represented in the workflow.

### Choreography

Participants react to failure events.

```text
             PaymentCompleted
                     |
                     v
             Inventory Service
                     |
                     | InventoryReservationFailed
                     v
               Event Broker
                     |
       +-------------+-------------+
       |                           |
       v                           v
Payment Service              Order Service
       |                           |
       v                           v
    Refund                    Mark Failed
```

The payment service must implement behavior that responds to inventory reservation failures, or another participant must own the compensation decision.

As workflows become more complex, failure-related dependencies can accumulate.

```text
PaymentCompleted
InventoryReservationFailed
PaymentRefundFailed
ShipmentCancelled
OrderCancellationFailed
CompensationRequested
```

This can make the global failure behavior difficult to reason about.

Both approaches can implement the **Saga pattern**, where a distributed business transaction is composed of local transactions and compensating operations.

**Neither approach automatically provides atomicity, isolation, exactly-once execution, or successful compensation.**

## 7. Global reasoning vs. local reasoning

Orchestration makes global reasoning easier because dependencies and workflow policies are explicitly represented.

```text
     A
     |
+----+----+
|         |
v         v
B         C
|         |
+----+----+
     |
     v
     D
```

An orchestrator can represent this structure as a directed acyclic graph (DAG).

It can determine that:

- B and C can execute concurrently.
- **D cannot execute until both B and C complete.**
- A failure in B may require cancelling C.
- Execution capacity can be allocated according to the critical path.

In choreography, the same logical DAG might exist implicitly.

```text
A Completed --+--> Service B
              +--> Service C

B Completed -----> Service D
C Completed -----> Service D
```

Service D must determine whether both prerequisites have completed, potentially maintaining additional coordination state.

As dependencies become more sophisticated, choreography can introduce distributed synchronization mechanisms that effectively recreate parts of an orchestrator.

## 8. Resource management and scheduling

Orchestration is particularly valuable when multiple operations compete for constrained resources.

Consider a distributed computation system:

```text
Workflow A --> 100 tasks
Workflow B --> 200 tasks
Workflow C --> 300 tasks

Available execution slots: 50
```

An orchestrator or associated scheduler with global visibility can implement:

| Mechanism           | Purpose                                   |
| ------------------- | ----------------------------------------- |
| Admission control   | Prevent excessive work from entering      |
| Scheduling          | Determine which task executes next        |
| Prioritization      | Allocate resources to important workloads |
| Concurrency control | Limit simultaneous execution              |
| Fairness            | Prevent workload starvation               |
| Backpressure        | Regulate upstream execution               |
| Cancellation        | Stop unnecessary work                     |
| Resource placement  | Improve locality and utilization          |

With choreography, individual participants can implement local resource management.

```text
Service A ---> Queue B ---> Service B
                                |
                                v
                             Queue C
                                |
                                v
                            Service C
```

Each stage can regulate its consumption rate, bound its queues, and apply backpressure.

However, local optimization does not necessarily produce globally optimal behavior.

Service A might continue producing work even though Service C is severely overloaded, unless congestion information propagates upstream or a broader coordination mechanism exists.

This distinction becomes important in distributed query engines, data processing platforms, cluster management systems, and inference infrastructure.

## 9. Scalability

A common misconception is that orchestration inherently limits scalability because it centralizes control.

**Logical centralization does not imply physical centralization.**

An orchestrator can be partitioned by workflow identity.

```text
   Incoming Workflows
            |
            v
   +----------------+
   | Router / Shard |
   +----------------+
            |
   +--------+--------+
   |        |        |
   v        v        v
+----+   +----+   +----+
| O1 |   | O2 |   | O3 |
+----+   +----+   +----+
   |        |        |
   +--------+--------+
            |
            v
   Distributed Workers
```

Each orchestrator instance owns a subset of workflows.

The coordination workload can scale independently from the execution workload.

Choreography can also scale horizontally through partitioned event streams and independent consumer groups.

```text
+-----------------------------------------------+
| Partitioned Log                               |
+---------------+---------------+---------------+
| Partition 0   | Partition 1   | Part 2        |
+---------------+---------------+---------------+
        |               |               |
        v               v               v
   Consumer 0      Consumer 1      Consumer 2
```

Both approaches have scalability constraints.

Orchestration may encounter workflow-state persistence bottlenecks, scheduling contention, and coordination overhead.

Choreography may encounter event amplification, partition skew, consumer lag, ordering constraints, and broker saturation.

## 10. Observability and debugging

Orchestration naturally provides a location for inspecting workflow progress.

```text
Workflow: order-123

Charge payment        SUCCESS     120ms
Reserve inventory     SUCCESS      80ms
Create shipment       RETRYING
Complete order        WAITING
```

Choreography requires reconstructing the causal relationships between distributed operations.

```text
Service A: Event published
Service B: Event consumed
Service B: Event published
Service C: Event consumed
Service C: Operation failed
```

This typically requires correlation IDs, distributed tracing, causation IDs, event histories, and materialized workflow views.

An observability system can reconstruct the global workflow without becoming responsible for coordinating it.

The challenge is not that choreographed systems are inherently unobservable. It is that **global visibility must be deliberately constructed rather than naturally residing in a workflow controller.**

## 11. Comparison

| Dimension                    | Orchestration              | Choreography                         |
| ---------------------------- | -------------------------- | ------------------------------------ |
| Coordination                 | Explicit                   | Emergent                             |
| Decision-making              | Logically centralized      | Distributed                          |
| Workflow definition          | First-class entity         | Implicit or externally modeled       |
| Global state                 | Usually explicitly tracked | Usually reconstructed or distributed |
| Failure handling             | Centralized policy         | Distributed reactions                |
| Dependency management        | Explicit                   | Implicit or locally enforced         |
| Global scheduling            | Easier                     | More difficult                       |
| Participant autonomy         | Moderate to high           | High                                 |
| Workflow observability       | More natural               | Requires additional infrastructure   |
| Adding independent consumers | May require changes        | Relatively easy                      |
| Complex branching            | Easier to manage           | Can become difficult to reason about |
| Scalability                  | Partitionable              | Naturally distributed                |
| Primary risk                 | Coordinator complexity     | Emergent behavioral complexity       |

## 12. When to use each approach

### Orchestration

Orchestration is particularly suitable when there is an identifiable unit of work with a defined lifecycle, complex dependencies, and a meaningful notion of completion.

Examples include:

| System                      | Unit of coordination                  |
| --------------------------- | ------------------------------------- |
| Distributed query engine    | Query execution                       |
| Kubernetes                  | Resource lifecycle and reconciliation |
| Batch processing platform   | Job execution                         |
| Workflow engine             | Business process                      |
| Distributed build system    | Build dependency graph                |
| Machine learning platform   | Training job                          |
| Infrastructure provisioning | Resource deployment                   |

Technologies such as Temporal, Apache Airflow, Kubernetes, and Argo Workflows implement various forms of orchestration.

### Choreography

Choreography is particularly suitable when independent components react to meaningful domain events and there is no requirement for a single component to own the entire resulting process.

```text
              OrderCompleted
                     |
    +----------------+-----------------+
    |                |                 |
    v                v                 v
Analytics         Loyalty        Notifications
 Service          Service           Service
```

Each consumer performs an independent operation.

Adding a recommendation service does not require modifying the order service or introducing a new workflow step into a coordinator.

```text
                       OrderCompleted
                              |
    +---------------+---------+-------+------------------+
    |               |                 |                  |
    v               v                 v                  v
Analytics        Loyalty        Notifications     Recommendations
```

This is a particularly effective use of choreography because the consumers do not collectively need to enforce a tightly coordinated execution lifecycle.

## 13. Hybrid architectures

Orchestration and choreography are not mutually exclusive.

A distributed system can use orchestration for its critical workflows and choreography for independent reactions to domain events.

```text
        +----------------------+
        | Order Orchestrator   |
        +----------------------+
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
 Payment        Inventory       Shipping
                                    |
                    +---------------+
                    |
                    v
             OrderCompleted
                    |
                    v
            +--------------+
            | Event Broker |
            +--------------+
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
Analytics     Notifications     Auditing
```

In this architecture:

The orchestrator owns the critical path, enforces dependencies, handles failures, and determines completion.

**Independent consumers react to the completion event without becoming part of the critical path.**

This prevents ancillary functionality from unnecessarily increasing workflow latency or reducing its availability.

## 14. Engineering principles

**Coordination complexity cannot be eliminated by distributing it.**

Removing an orchestrator does not remove dependencies, ordering constraints, synchronization requirements, failure handling, or consistency requirements. It changes where those responsibilities reside.

**Centralize policy, distribute execution.**

When operations require global scheduling, resource allocation, or consistent failure policies, logically centralized coordination can substantially simplify the system without centralizing computational work.

**Asynchronous execution and orchestration are compatible.**

An orchestrator does not need to synchronously block while waiting for operations. It can persist state, dispatch commands, consume completion events, and resume execution.

**Autonomy is most valuable when operations are genuinely independent.**

Choreography provides its greatest benefits when participants can evolve, fail, and scale independently without violating global invariants.

**Keep coordination off the expensive data path.**

An orchestrator should generally exchange control messages and metadata rather than proxying large volumes of application data between workers.

## Mental model

```text
ORCHESTRATION

  Explicit global plan
            |
            v
  Distributed execution

CHOREOGRAPHY

   Distributed local rules
              |
              v
  Emergent global behavior
```

Orchestration treats the workflow as a first-class abstraction. Choreography treats autonomous participants and their interactions as first-class abstractions.

The architectural decision ultimately depends on whether **global coordination or local autonomy is the more important property of the system**.
