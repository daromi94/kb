# Deadline propagation

A deadline is an absolute point in time by which a request must
finish — "complete by 14:30:05," not "wait five seconds." The edge
stamps each request with `deadline = now + budget`, and every
downstream hop forwards what's left rather than starting a fresh
per-hop timeout.

## Risks

A request without a deadline runs until something else stops it —
the service's worst-case timeout, an exhausted connection pool, a
crashed process. The costs pile up before any of those trip:

- **Resources stay held** — connections, thread slots, and buffers
  locked per in-flight request for the full window.
- **Memory pressure climbs** as long-running requests accumulate.
- **Queues grow** as new work arrives faster than slow requests
  retire.
- **The process crashes** when memory or connections exhaust.

## Per-hop timeouts don't compose

A five-deep call tree with a 100 ms timeout at each hop accepts up to
500 ms of work for a request the user abandoned at 100 ms. Each layer
enforces only its own slice; nobody sees the request's total budget.
A propagated deadline shrinks as the request travels, so every hop
abandons work it cannot finish in time. Per-hop timeouts sum;
deadlines compose.

## On the wire

Clocks across machines disagree by more than network transit time, so
an absolute timestamp on the wire would be misread on arrival. Each
side stores the deadline against its own clock; the wire carries a
remaining duration, computed just before sending and converted back
to an absolute deadline on arrival. The reconstruction is off by one
network transit at most, not by however far the clocks differ.

Each hop should also reserve a slice of the budget for its own
processing before forwarding. Otherwise, the downstream call starts
with a deadline about to expire, leaving no time to act on the
response.

## Reject expired work at dequeue

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
