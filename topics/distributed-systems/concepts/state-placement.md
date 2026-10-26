# State placement

A fundamental architectural decision in distributed dataflow systems is where to store application state relative to the computation that accesses it.

This decision affects three important properties:

1. Performance: How quickly tasks can access and update state.
2. Adaptability: How easily tasks can be scaled, moved, or reorganized.
3. Operational disruption: How much ongoing computation is affected when the system changes.

The central tension is that placing state close to computation improves performance, but makes computation harder to move independently of that state.

## 1. What is state in a dataflow system?

A distributed dataflow system executes computations organized as a directed graph of operators.

Consider an application that continuously counts transactions per customer.

```
                Input Stream
                     |
                     v
             +---------------+
             | Parse Records |
             +---------------+
                     |
                     v
             +---------------+
             | Partition by  |
             | Customer ID   |
             +---------------+
                     |
              +------+------+
              |             |
              v             v
         +---------+   +---------+
         | Task A  |   | Task B  |
         |         |   |         |
         | Count   |   | Count   |
         +---------+   +---------+
              |             |
              +------+------+
                     |
                     v
                Output
```

Each task processes a subset of customer IDs.

For example:

```
Task A                    Task B
------------------        ------------------
Customer 1: 120           Customer 3: 250
Customer 2:  80           Customer 4:  90
```

The customer counters constitute application state.

Unlike a stateless transformation, which can process each input independently, a stateful operator needs information accumulated from previous records.

For every incoming transaction, the appropriate task must:

1. Read the customer's current counter.
2. Increment it.
3. Write the updated counter.
4. Potentially produce an output.

Consequently, the placement of this state directly influences the cost of processing each record.

## 2. Embedded state: computation and state together

In an embedded-state architecture, each task maintains its assigned state locally.

```
               Worker Node 1
       +-----------------------------+
       |                             |
       |   +---------------------+   |
       |   | Task A              |   |
       |   |                     |   |
       |   | Computation         |   |
       |   |      |              |   |
       |   |      v              |   |
       |   | Local State         |   |
       |   | Customer 1: 120     |   |
       |   | Customer 2:  80     |   |
       |   +---------------------+   |
       |                             |
       +-----------------------------+
```

State might be maintained in memory, a local embedded key-value database, or a combination of memory and local disk.

### Why is this fast?

A record can be processed without making a network request to retrieve its state.

```
Record arrives
      |
      v
Read local state
      |
      v
Perform computation
      |
      v
Update local state
      |
      v
Emit result
```

The main advantages are low state-access latency, reduced network traffic, and generally efficient resource utilization.

However, a problem emerges when the system needs to change its execution topology.

### What happens during scaling?

Suppose Task A becomes overloaded.

The system decides to split its workload between Task A and a new Task C.

Before:

```
Task A
+----------------------+
| Customer 1           |
| Customer 2           |
| Customer 3           |
| Customer 4           |
+----------------------+
```

After:

```
Task A                    Task C
+------------------+      +------------------+
| Customer 1       |      | Customer 3       |
| Customer 2       |      | Customer 4       |
+------------------+      +------------------+
```

Task C now owns customers 3 and 4.

But their state is still stored inside Task A.

```
Task A                          Task C
+--------------------+          +--------------------+
| Customer 1         |          |                    |
| Customer 2         |          |                    |
| Customer 3 --------+--------->| Customer 3         |
| Customer 4 --------+--------->| Customer 4         |
+--------------------+          +--------------------+

             State migration
```

In a conventional embedded-state architecture, the state must be transferred before Task C can independently process those customers.

This introduces several costs:

- Network bandwidth consumed by state migration.
- CPU utilization for serialization and deserialization.
- Disk I/O for reading and writing state.
- Synchronization to prevent concurrent updates to the same state.
- Possible processing stalls and backlog accumulation.

The larger the state, the more expensive reconfiguration can become.

For example, a task might process only a few thousand records per second but own hundreds of gigabytes of accumulated state.

Moving the computation is cheap. Moving its associated state is potentially expensive.

## 3. External state: computation and state separated

An alternative architecture separates computation from storage.

Tasks become clients of an independent state service.

```
             Compute Layer

     +----------+      +----------+
     | Task A   |      | Task B   |
     +----------+      +----------+
          |                 |
          |  Network RPCs   |
          |                 |
          +--------+--------+
                   |
                   v
         +--------------------+
         | Shared State Store |
         |                    |
         | Customer 1: 120    |
         | Customer 2:  80    |
         | Customer 3: 250    |
         | Customer 4:  90    |
         +--------------------+
```

Here, the state is not physically tied to the computational task.

This fundamentally changes reconfiguration.

### Scaling becomes much easier

Suppose Task A is overloaded.

A new Task C is introduced and assigned some of Task A's customers.

```
BEFORE

Task A ----+
           |
           v
      State Store


AFTER

Task A ----+
           |
Task C ----+----> State Store
```

No application state needs to move between computational tasks merely because responsibility for a set of keys has changed.

The system updates routing and ownership assignments, and Task C starts accessing the existing state.

This is a significant advantage for long-running applications requiring frequent scaling or workload rebalancing.

### What is the cost?

Every state access may now involve a network operation.

```
Record arrives
      |
      v
Send remote state request
      |
      v
Wait for network + storage
      |
      v
Receive state
      |
      v
Perform computation
      |
      v
Write updated state remotely
      |
      v
Emit result
```

Compared with local state, this introduces network latency, serialization overhead, and additional load on the storage infrastructure.

Batching, caching, and asynchronous I/O can mitigate these costs, but they add complexity and do not eliminate the underlying trade-off.

Thus, external state offers greater flexibility at the potential expense of steady-state performance.

## 4. Why long-running applications make this trade-off especially important

Consider a stream-processing application that runs continuously for months.

During its lifetime, workload characteristics may change significantly.

```
Time -------------------------------------------------->

Morning       Afternoon       Evening        Night

Low load      High load       Medium load    Low load

4 tasks  ---> 12 tasks  ----> 8 tasks  ----> 4 tasks
```

Each change in task count may require redistributing the key space.

Additionally, reconfiguration can happen for reasons unrelated to scaling:

| Reconfiguration       | Purpose                                     |
| --------------------- | ------------------------------------------- |
| Scale-out             | Add tasks to increase processing capacity   |
| Scale-in              | Remove tasks to reduce resource consumption |
| Rebalancing           | Redistribute keys to reduce load imbalance  |
| Task migration        | Move computation to another worker          |
| Resource reallocation | Adapt execution to available infrastructure |

In an embedded-state architecture, changes in task ownership or placement can trigger state migration.

In an external-state architecture, computation can often be reorganized without physically moving application state.

This makes the cost of reconfiguration an important consideration, not merely the performance of the system under a fixed configuration.

## 5. The architectural trade-off

| Property                   | Embedded state          | External state         |
| -------------------------- | ----------------------- | ---------------------- |
| State access latency       | Usually lower           | Usually higher         |
| Network traffic per access | Low                     | Higher                 |
| Steady-state performance   | Generally better        | Remote-access overhead |
| Scaling flexibility        | Requires state handling | Easier                 |
| Task migration             | Potentially expensive   | Usually simpler        |
| Reconfiguration disruption | Potentially significant | Generally lower        |

The key distinction is between steady-state efficiency and reconfiguration efficiency.

An architecture optimized for processing records efficiently may struggle when workload ownership changes. An architecture optimized for changing task assignments may incur a continuous cost during record processing.

## 6. The deeper distributed systems principle: ownership versus location

There are two concepts that are often treated as equivalent but are fundamentally different.

Logical ownership determines which task is responsible for processing and updating a key.

Physical location determines where the state associated with that key is actually stored.

Consider:

```
                  Logical Ownership

                  Key 42
                     |
                     v
                  Task B


                  Physical Location

                  Key 42
                     |
                     v
                  Task A
```

Task B owns key 42, but Task A still physically stores its state.

This arrangement is possible if the system maintains metadata describing the physical location and guarantees exclusive state access.

For example:

```
                      Task B
                    (Key owner)
                         |
                         | Lookup Key 42
                         v
                  +---------------+
                  | Location Map  |
                  | 42 -> Task A  |
                  +---------------+
                         |
                         | Fetch state
                         v
                      Task A
                  (State holder)
```

This decoupling introduces an interesting design opportunity:

- Task ownership can change immediately.
- Physical state can remain at its previous location.
- State can be moved only when necessary.
- Once fetched, subsequent accesses can be local.

However, it also introduces correctness challenges: there must never be two tasks concurrently updating the same key, even while ownership and location are changing.

## 7. Key engineering insight

Moving responsibility for computation does not inherently require moving the data used by that computation.

Traditional embedded-state systems often couple the two operations:

```
Reconfiguration
       |
       v
Move computation ownership
       |
       v
Move associated state
       |
       v
Resume processing
```

A decoupled design allows the operations to happen independently:

```
Reconfiguration
       |
       v
Transfer logical ownership
       |
       v
Continue processing
       |
       +----------------------+
       |                      |
       v                      v
Local state access      Remote state access
                              |
                              v
                       Migrate if needed
```

This design shifts the fundamental question from:

How can all the state be migrated quickly?

to:

How much state actually needs to be migrated at all?

That distinction is especially important for large, long-running stateful systems, where the total accumulated state can be enormous while only a small fraction of keys is actively accessed.

The broader distributed systems lesson is that decoupling logical responsibility from physical resource placement can improve adaptability without necessarily sacrificing locality during normal operation.
