# Postmortem anatomy

A high-quality correction of errors (COE) document digs through
multiple layers of system and organizational failure. It never stops
at the most proximal cause.

## Start with observability

Verify exactly what happened from data, not from assumptions or
recollections. If you cannot definitively prove what happened, the
first lesson is that your logging, metrics, or tracing are
insufficient — and fixing that becomes an action item in its own
right.

## Interrogate the whys at multiple levels

A code bug is never the whole story. Push further:

- Why did testing miss it?
- Why did the validation process assume the system would behave that
  way?
- What team or social processes created those blind spots?

Each layer — technical, process, social — is a distinct place where a
fix can be applied. Stopping at the first answer leaves the other
layers untouched and the same class of failure ready to return.

## Multi-tiered action items

Fixes must address every layer the investigation surfaced:

| Layer   | Fix                                             |
|---------|-------------------------------------------------|
| Code    | The specific line or module that failed         |
| Testing | The test that should have caught it             |
| Process | The human workflow that allowed the gap to ship |

An action list that only patches the code has learned from only one
layer.

---

Return to [SRE](_index.md)
