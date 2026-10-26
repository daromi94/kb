# Ownership vs location

Ownership and location are two independent concepts: ownership determines who is responsible for a resource, while location determines where that resource physically resides.

Separating these concepts is a powerful architectural technique because it allows a distributed system to change responsibility for data without necessarily moving the data itself.

## 1. Understanding the distinction

Consider a distributed system that maintains state for millions of customers.

Each customer has a key and associated state:

```text
Key: customer-42

State:
  balance: 1500
  transactions: 230
```

Two questions arise:

Ownership: Who is allowed to process this customer?

```text
customer-42
   |
   v
+--------+
| Task B |
+--------+

Logical owner
```

Task B is responsible for processing records associated with `customer-42`.

Location: Where are the actual bytes stored?

```text
customer-42
   |
   v
+--------+
| Task A |
|        |
| State  |
+--------+

Physical location
```

Task A physically stores the customer's state.

These assignments can differ.

```text
             customer-42
                  |
          +-------+-------+
          |               |
          v               v
      Ownership        Location
          |               |
          v               v
       Task B           Task A
```

The distinction is:

- Ownership is about authority and responsibility.
- Location is about physical storage and data access.

In a stateful dataflow system, logical ownership typically establishes which task has exclusive responsibility for reading, processing, and updating a key's state.

Physical location determines whether accessing that state requires local storage access or network communication.

## 2. Why are ownership and location traditionally coupled?

Many distributed dataflow systems enforce the following relationship:

```text
Owner(key) == Location(key)
```

Consider a stateful operator with two tasks.

```text
+---------------------+
| Task A              |
|                     |
| Owns keys: 1, 2     |
|                     |
| Stores state: 1, 2  |
+---------------------+

+---------------------+
| Task B              |
|                     |
| Owns keys: 3, 4     |
|                     |
| Stores state: 3, 4  |
+---------------------+
```

This design is attractive because it provides two benefits.

Efficient state access: Tasks can access their own state locally without network communication.

Simple concurrency control: Each key has a single owner, so different tasks can process their respective keys without coordinating every state update.

However, this coupling becomes problematic during reconfiguration.

Suppose key 2 is reassigned from Task A to Task B.

Under a tightly coupled design, Task B cannot independently start processing key 2 until its associated state has been moved.

```text
Before:

Task A                       Task B
+----------------+           +----------------+
| Owner: 1, 2    |           | Owner: 3, 4    |
| State: 1, 2    |           | State: 3, 4    |
+----------------+           +----------------+


Reconfiguration:

Task A                       Task B
+----------------+           +----------------+
| State: 1, 2    |--- 2 ---->| State: 2, 3, 4 |
+----------------+           +----------------+


After:

Task A                       Task B
+----------------+           +----------------+
| Owner: 1       |           | Owner: 2, 3, 4 |
| State: 1       |           | State: 2, 3, 4 |
+----------------+           +----------------+
```

Changing ownership becomes dependent on physically migrating state.

If the reassigned partition contains 100 GB of state, the system may need to move a substantial amount of data before completing the transition.

## 3. Decoupling ownership from location

A different architecture permits:

```text
Owner(key) != Location(key)
```

The system can reassign a key to a new task while leaving its state on the previous task.

Consider the same example.

### Step 1: Initial configuration

```text
Task A                       Task B
+----------------+           +----------------+
|                |           |                |
| Owns: 1, 2     |           | Owns: 3, 4     |
|                |           |                |
| Stores: 1, 2   |           | Stores: 3, 4   |
+----------------+           +----------------+
```

### Step 2: Transfer logical ownership

Key 2 is reassigned to Task B.

However, its state remains on Task A.

```text
Task A                       Task B
+----------------+           +----------------+
|                |           |                |
| Owns: 1        |           | Owns: 2, 3, 4  |
|                |           |                |
| Stores: 1, 2   |           | Stores: 3, 4   |
+----------------+           +----------------+
         ^
         |
         +---- State for key 2 remains here
```

Notice that ownership changed without any state migration.

Task B is now responsible for key 2, although Task A still holds its physical state.

### Step 3: Access state remotely

When Task B receives a record for key 2, it must retrieve the corresponding state.

```text
Task B
(Owner of 2)
   |
   | Fetch state for key 2
   |
   v
Task A
(Stores key 2)
   |
   | Return state
   |
   v
Task B
   |
   v
Process record
```

Once Task B has fetched the state, it can store it locally and process subsequent records without remote access.

```text
Task A                       Task B
+----------------+           +----------------+
|                |           |                |
| Owns: 1        |           | Owns: 2, 3, 4  |
|                |           |                |
| Stores: 1      |           | Stores: 2, 3, 4|
+----------------+           +----------------+
```

The important difference is that state migration occurs when the state is needed, rather than when ownership changes.

This is called lazy state migration.

## 4. How can the new owner locate state?

Once ownership and location are independent, routing incoming records is no longer sufficient to locate their state.

The system needs separate metadata.

Consider two logical mappings.

Ownership mapping

```text
Key      Owner
----------------
1        Task A
2        Task B
3        Task B
4        Task B
```

State location mapping

```text
Key      Location
----------------
1        Task A
2        Task A
3        Task B
4        Task B
```

The first mapping determines where records should be processed.

The second determines where the required state can be retrieved.

These mappings need not be centralized. A task can maintain state-location information for only the keys it owns.

Consider processing an event for key 2:

```text
Incoming record
key = 2
   |
   v
Routing Table
   |
   v
Task B
   |
   v
Location Lookup
   |
key 2 -> A
   |
   v
Fetch from A
   |
   v
Store locally
   |
   v
Process event
```

After migration, Task B updates its location metadata:

```text
Before: key 2 -> Task A
After:  key 2 -> Task B
```

Future accesses are local.

## 5. Ownership is fundamentally a concurrency-control mechanism

This is the most important correctness implication.

Suppose Task B becomes the new owner of key 2 while Task A still physically stores its state.

What prevents both tasks from modifying that state simultaneously?

The answer is exclusive logical ownership.

A useful invariant is:

```text
For every key k: count(Owners(k)) = 1
```

Every key has exactly one logical owner at any moment.

During ownership transfer, the old owner must finish its existing operations before the new owner starts processing that key.

```text
Time -------------------------------------------------->

Task A:
  Process key 2
  Update state
  Finish current batch
  Transfer ownership
            |
            v
      Stop processing key 2


Task B:
            |
            v
      Acquire ownership
      Fetch state if remote
      Process key 2
```

Task A may continue to serve the stored state to Task B, but it must no longer independently process records or modify that key as its logical owner.

This distinction enables safe remote storage access without requiring distributed locks for every event.

The ownership handoff itself must still be synchronized correctly.

### What about records already in flight?

Suppose upstream producers still send records to Task A after ownership has moved to Task B.

Those records cannot be processed by Task A.

Instead, Task A forwards them to the new owner.

```text
Upstream
   |
   | Old routing information
   v
Task A
   |
   | Forward key 2
   v
Task B
   |
   v
Process key 2
```

Eventually, upstream routing is updated, so new records reach Task B directly.

The old forwarding path can be retired once all relevant in-flight records have been drained.

This preserves correctness while allowing routing and state location to change at different times.

## 6. A more subtle consequence: ownership can move repeatedly

Consider three tasks: A, B, and C.

Initially, Task A owns and stores key 42.

After the first reconfiguration:

```text
Owner(42)    = Task B
Location(42) = Task A
```

Assume Task B never accesses key 42, so no state migration occurs.

A second reconfiguration assigns key 42 to Task C.

```text
Owner(42)    = Task C
Location(42) = Task A
```

Notice that Task B never physically stored the state.

An inefficient design might discover the state by following historical ownership:

```text
Task C ---> Task B ---> Task A
```

Instead, location metadata can be transferred along with ownership.

Task C receives the actual location information:

```text
Key 42 -> Task A
```

It can fetch directly:

```text
Task C -------------------> Task A
       direct state fetch
```

This is a single-hop state lookup, regardless of how many times the key has changed owners.

It prevents repeated reconfiguration from increasing the network distance needed to locate a key.

## 7. Why is this separation valuable?

Consider a system containing 1 TB of state, distributed among multiple workers.

A reconfiguration redistributes responsibility for 200 GB of that state.

However, suppose only 5 GB of the reassigned state is actively accessed afterward.

With eager migration:

```text
Ownership transferred: 200 GB worth of keys
State migrated:        200 GB
```

With lazy migration:

```text
Ownership transferred: 200 GB worth of keys
State migrated:          5 GB
State left in place:   195 GB
```

These are illustrative numbers.

The advantage comes from exploiting temporal locality: large stateful applications often have a small active working set relative to their total accumulated state.

There are limitations, however. If the worker storing the cold state must be removed, that state eventually needs another storage location. Likewise, workloads that access nearly every key may end up migrating most of the reassigned state.

## 8. The broader architectural principle

Separating ownership from location creates two independently evolving dimensions:

| Dimension         | Governs                         | Primary concern                          |
| ----------------- | ------------------------------- | ---------------------------------------- |
| Logical ownership | Who processes and updates a key | Correctness, concurrency, load balancing |
| Physical location | Where the key's state resides   | Locality, I/O latency, storage placement |

The same principle appears in other distributed system designs, including primary-replica architectures, distributed caches, and storage systems that separate metadata management from physical data placement. The exact semantics of ownership differ across those systems.

The central insight is:

Ownership is a logical decision about authority. Location is a physical decision about data placement.

When these are tightly coupled, changing authority often requires expensive data movement.

When they are decoupled, the system can reorganize computation rapidly, defer unnecessary movement, and preserve local access for frequently used state.

The engineering challenge then shifts from bulk migration to maintaining three invariants: a single logical owner per key, accurate state-location metadata, and correct record delivery during ownership transitions.
