# Deadline propagation

A deadline is an absolute point in time by which a request must
finish — "complete by 14:30:05," not "wait five seconds." The edge
service stamps each request with `deadline = now + budget` to fix
the target.

The deadline carries through every downstream call. Each hop
subtracts elapsed time and forwards the remainder, not a fresh
per-hop timeout.

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

Clocks across machines disagree by more than network transit time,
so an absolute timestamp on the wire would be misread on arrival.
Each side keeps the deadline as an absolute timestamp locally; the
wire carries a remaining duration, computed just before sending and
converted back to an absolute deadline against the receiver's clock
on arrival. The reconstruction is off by one network transit at
most, not by however far the clocks differ.

Each hop should also subtract a small local processing budget before
forwarding. Otherwise, the downstream call starts with a deadline
already about to fire on the caller, leaving no time to act on the
response.

## Reject when the budget is gone

A worker that picks up a request whose budget has expired is about to
do work nobody will read. Check the budget at dequeue and fail the
request when it cannot cover the estimated cost. Under overload this
is decisive: rejecting at the door keeps the queue moving, while
starting work and canceling it midway burns resources anyway.

## Related

- [Cooperative cancellation](cooperative-cancellation.md) - Actually stopping the work
- [Fanout tail amplification](fanout-tail-amplification.md) - Why deep trees need this
- [Tail-targeted engineering](tail-targeted-engineering.md) - Variance-reduction toolkit

---

Return to [Latency](_index.md)
