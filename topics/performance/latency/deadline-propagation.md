# Deadline propagation

A request stamped with `deadline = now + budget` carries that deadline
through every downstream call. Each hop subtracts elapsed time and
forwards the remainder, not a fresh per-hop timeout.

## Risks

Without a deadline, a request runs until the service's maximum. The
costs compound:

- **Resources stay held** — connections, thread slots, and buffers
  locked per in-flight request for the full window.
- **Memory pressure climbs** as long-running requests accumulate.
- **Queues grow** as new work arrives faster than slow requests
  retire.
- **The process crashes** when memory or connections exhaust.

## Why deadlines beat per-hop timeouts

A five-deep call tree with a 100 ms timeout at each hop will accept up
to 500 ms of work for a request the user abandoned at 100 ms. With a
propagated 100 ms deadline, every hop sees a budget that has already
shrunk and abandons work it cannot finish in time. Per-hop timeouts
sum; deadlines compose.

## Forwarding

A deadline is conceptually an absolute timestamp, but clocks across
machines disagree by more than network transit time — an absolute
timestamp on the wire would be misread on arrival. Ship a remaining
duration instead; the receiver reconstructs the deadline against its
own clock. The reconstruction is off by one network transit at most,
not by however far the clocks differ.

Each hop should also subtract a small local processing budget before
forwarding. Otherwise, the downstream call starts with a deadline
already about to fire on the caller, leaving no time to act on the
response.

## Reject when the budget is gone

A worker that picks up a request whose budget has expired is about to
do work nobody will read. Check the budget at dequeue and fail the
request when it cannot cover the estimated cost. Under overload this
is decisive: rejecting at the door keeps the queue moving, while
starting work and canceling it midway burns the CPU anyway.

## Related

- [Cooperative cancellation](cooperative-cancellation.md) - Actually stopping the work
- [Fanout tail amplification](fanout-tail-amplification.md) - Why deep trees need this
- [Tail-targeted engineering](tail-targeted-engineering.md) - Variance-reduction toolkit

---

Return to [Latency](_index.md)
