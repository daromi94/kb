# Crash-only software

Crash-only software is built so the only way to stop it is to crash it,
and the only way to recover is to restart. Making a crash safe at any
moment imposes five structural properties on the system.

## The five properties

1. All important non-volatile state is managed by dedicated state stores.
2. Components have externally enforced boundaries.
3. All interactions between components have a timeout.
4. All resources are leased, rather than permanently allocated.
5. Requests are entirely self-describing.

## State lives in dedicated stores

Either commit to storing data safely in a system built for it, or
explicitly accept that the data is volatile. Half-measures — state that
is kept in application memory but treated as if it will persist — are
the trap. A crash must either leave the data intact in its store or
destroy it cleanly, with no middle ground that silently corrupts.

## Boundaries are externally enforced

Components interact through well-defined APIs and nothing else. Implicit
communication channels — shared memory, globals, side effects on common
infrastructure — are minimized or removed. The boundary is enforced from
outside the component so a misbehaving component cannot reach past it.

## Every interaction has a timeout

Operations can fail. Waiting indefinitely for a component that may never
respond is not resilience; it is a resource leak waiting to exhaust the
caller. Bounded waits turn silent hangs into explicit failures the
caller can handle.

## Resources are leased

Resources — locks, connections, memory, handles — are handed out for a
bounded time and reclaimed when the holder no longer justifies keeping
them. Leases remove the need for a cooperative shutdown: if the holder
dies mid-operation, the lease expires and the resource returns to the
pool on its own.

## Requests are self-describing

A request carries the context needed to process it rather than relying
on implicit protocol state held by the server. Self-describing requests
survive server restarts, route freely between instances, and remove a
large class of subtle bugs where client and server disagree about what
state the conversation is in.

---

Return to [Concepts](_index.md)
