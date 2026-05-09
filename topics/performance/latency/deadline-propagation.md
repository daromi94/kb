# Deadline propagation

A deadline is an absolute point in time by which a request must
finish — "complete by 14:30:05," not "wait five seconds." The edge
stamps each request with `deadline = now + budget`. Every downstream
hop forwards what's left, not a fresh per-hop timeout.

## Risks

Without a deadline, a request runs to the service's worst-case
timeout — long after the caller has given up. The damage piles up
while it does:

- **Resources stay held** — connections, thread slots, and buffers
  remain locked.
- **Memory pressure climbs** as long-running requests accumulate.
- **Queues grow** as new work arrives faster than slow requests
  retire.
- **The process crashes** when memory or connections run out.

## Per-hop timeouts don't compose

In a five-deep call tree with a 100 ms timeout at each hop, a single
request can keep work alive for up to 500 ms — long after the user
gave up at 100 ms. Each layer enforces only its own slice; nobody
sees the total budget. A propagated deadline shrinks as the request
travels, so every hop drops work it cannot finish. Per-hop timeouts
sum; deadlines compose.

## On the wire

Clocks on different machines disagree by more than the network
transit time between them, so an absolute timestamp on the wire would
be misread on arrival. Instead, each side holds the deadline as a
local timestamp, and the wire carries the remaining duration. The
sender computes that duration just before transmitting; the receiver
converts it back to an absolute deadline against its own clock. The
result is off by one network transit at most.

## Reserve a per-hop slice

Each hop should reserve a slice of the budget for its own processing
before forwarding. Otherwise, the downstream call starts with a
deadline about to expire, leaving no time to act on the response.

## Reject expired work at dequeue

A worker that picks up a request whose budget has expired is about to
do work nobody will read. Check the budget at dequeue and fail the
request when it cannot cover the estimated cost. Under overload this
is decisive: rejecting at the door keeps the queue moving, while
starting work and canceling it midway burns resources anyway.

---

Return to [Latency](_index.md)
