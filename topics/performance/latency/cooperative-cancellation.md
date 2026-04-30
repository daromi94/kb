# Cooperative cancellation

A cancel signal does not stop work — it asks the receiver to stop.
Closing a connection frees the channel, not the CPU. To halt fanout
on a deadline, every worker must observe the signal and return.

## The cancellation tree

A coordinator owns a root cancel token; each fanout worker derives a
child. Canceling the root cancels every descendant. Children cannot
cancel their parent — signals flow down only. The pattern shows up
across runtimes as Go's `context.Context`, Rust's
`CancellationToken`, and structured-concurrency scopes elsewhere.

## Three triggers cancel siblings

- **Global deadline expires** — coordinator cancels the root.
- **First success in a hedged set** — winner cancels losers.
- **Fatal error from any worker** — no point continuing when the
  result is already unusable.

## Workers must poll

The runtime cannot interrupt arbitrary application code. A worker
that does not check the cancel signal between I/O steps keeps
burning CPU after the deadline, no matter how good the upstream
signaling is. A long CPU loop without polling is functionally
uncancellable.

## Cancel-after-commit

Side effects already begun — DB writes, external API calls — do not
roll back when the cancel arrives. Idempotency keys make a
cancel-after-commit survivable on retry rather than catastrophic.

## Related

- [Deadline propagation](deadline-propagation.md) - The signal that triggers cancel
- [Fanout tail amplification](fanout-tail-amplification.md) - Why fanouts need this
- [Tail-targeted engineering](tail-targeted-engineering.md) - Hedged and tied requests

---

Return to [Latency](_index.md)
