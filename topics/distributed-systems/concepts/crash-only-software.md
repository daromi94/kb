# Crash-only software

Crash-only software treats abrupt termination as its normal stop path and
restart as its only recovery path. Five structural constraints make this
safe by moving durability, isolation, cleanup, and request context outside
the lifetime of the process.

> **A component can stop without cooperation only when correctness does
> not depend on its shutdown code.**

## A crash cannot depend on cleanup

A conventional shutdown path may flush buffers, release locks, and notify
peers before the process exits. A crash can interrupt the process before
any of those actions complete. Crash-only software therefore assumes that
none of them run.

Its lifecycle has no separate graceful stop path:

```text
+---------+    crash    +---------+    restart    +---------+
| Running | ----------> | Stopped | ------------> | Running |
+---------+             +---------+               +---------+
```

This lifecycle creates a strict design test: if the process disappears at
any instruction, another instance must continue without guessing what the
failed process left behind.

## Durable state outlives the process

Important nonvolatile state belongs in a dedicated state store. Process
memory is either explicitly volatile or reconstructible from that store.
The design does not treat in-memory state as though it survives a restart.

This separation gives every piece of state a clear fate. Durable state
remains intact in its store, while volatile state can disappear without
damaging correctness. Restart reconstructs what the process needs instead
of recovering an ambiguous partial state.

## External boundaries contain failure

Externally enforced boundaries limit what a failed component can affect.
Components communicate through defined interfaces instead of shared
memory, global variables, or implicit side effects on common
infrastructure.

The enforcement must live outside the component. A process that fails or
misbehaves cannot be trusted to preserve its own boundary, but an external
boundary continues to constrain it.

## Timeouts turn silence into failure

Every interaction has a timeout because a crashed component cannot send a
final response. Without a timeout, its callers may wait forever and retain
threads, connections, or memory for work that cannot complete.

A bounded wait converts silence into an explicit failure. The caller can
then release its own resources, retry through another instance, or return
the failure to its caller.

## Leases reclaim abandoned resources

A lease grants a resource for a bounded period instead of allocating it
permanently. Locks, connections, memory, and handles return to their pools
unless the holder renews them.

If a process crashes mid-operation, it stops renewing its leases. Each
lease eventually expires, so the system reclaims the resource without
running cleanup code in the failed process.

## Requests carry their own context

A self-describing request contains the context required to process it. It
does not depend on conversation state stored only inside one server
process.

After a crash, the same request can reach another instance without first
reconstructing an implicit session. This keeps the client and server from
disagreeing about the state of an interrupted exchange.

## The constraints work together

The five constraints move each recovery responsibility outside the process:

```text
                              durable write
+----------+    request    +------------------+    +-------------+
| Caller   | ------------> | Crash-only       | -> | State store |
| timeout  | <------------ | process          |    | durable     |
+----------+    response   +--------+---------+    +-------------+
                                   |
                                   | acquire or renew lease
                                   v
                          +-------------------+
                          | Resource pool     |
                          | expiring leases   |
                          +-------------------+
```

If the process crashes, the caller's timeout ends the wait, the state store
retains durable data, and the resource pool expires abandoned leases. A
self-describing request can then run on a replacement inside the same
externally enforced boundary.

Crash-only design does not make crashes harmless. It makes recovery
independent of the failed process by ensuring that everything needed to
continue already lives outside it.

---

Return to [Concepts](_index.md)
