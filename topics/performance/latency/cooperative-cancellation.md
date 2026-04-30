# Cooperative cancellation

A cancel signal does not stop work — it asks the receiver to stop.
Closing the connection frees the wire, not the work. Cancellation is
cooperative: the runtime delivers the signal; only the worker can
stop the work.

## The cancellation tree

A coordinator owns a root cancel token; each fanout worker derives a
child. Canceling the root cancels every descendant. Children cannot
cancel their parent — signals flow down only. The tree gives mass
cancel for free: one signal reaches every descendant.

## When to cancel siblings

- **Global deadline expires** — coordinator cancels the root.
- **First success in a hedged set** — winner cancels losers.
- **Fatal error from any worker** — coordinator cancels the rest;
  the result is unusable.

## Workers must poll

The runtime cannot interrupt arbitrary application code. A worker
that does not check the cancel signal between steps runs to
completion, burning resources for a result nobody will read. A loop
without polling is functionally uncancellable.

## What cancel cannot undo

Side effects already begun — DB writes, external API calls — do not
roll back when the cancel arrives. Idempotency keys make a canceled
side effect survivable on retry rather than catastrophic.

## Related

- [Deadline propagation](deadline-propagation.md) - The signal that triggers cancel
- [Fanout tail amplification](fanout-tail-amplification.md) - Why fanouts need this
- [Tail-targeted engineering](tail-targeted-engineering.md) - Hedged and tied requests

---

Return to [Latency](_index.md)
