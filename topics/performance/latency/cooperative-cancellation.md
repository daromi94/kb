# Cooperative cancellation

A cancel signal does not stop work — it asks the worker to stop.
Closing the connection frees the wire, not the work. Cancellation
is cooperative: the runtime delivers the signal; only the worker
can act on it.

## Workers must poll

The runtime cannot interrupt arbitrary code. A worker that does not
check the cancel signal between steps runs to completion, burning
resources on a result nobody will read. A loop without polling is
uncancellable.

## When to cancel

- **Deadline expires** — cancel anything still running.
- **Fatal error** — cancel the rest; the result is unusable.
- **Hedge winner returns** — cancel the losers.

## Side effects don't undo

Side effects already begun do not roll back — DB writes, external
API calls. Idempotency keys make a canceled side effect safe to
retry.

## Related

- [Deadline propagation](deadline-propagation.md) - The signal that triggers cancel
- [Fanout tail amplification](fanout-tail-amplification.md) - Why fanouts need this
- [Tail-targeted engineering](tail-targeted-engineering.md) - Hedged and tied requests

---

Return to [Latency](_index.md)
