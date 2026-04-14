# On-call as learning

On-call is the bridge between theory and production reality. Treat
rotations as the primary mechanism for engineers to see how the system
actually behaves under load — not as a queue of tickets to close.

## Automate the rote

If an engineer closes the same ticket more than once, that work should
be automated. Repeat tickets signal a missing tool or guardrail, not a
need for a human. A rotation drowning in routine tickets is a rotation
with nothing left to learn.

## Investigate the unexpected

Experts are placed on call to spend bandwidth on unusual behavior,
edge cases, and unanticipated customer usage. The value comes from
deep investigation of anomalies that monitoring cannot explain by
itself.

Without this framing, on-call becomes rote work that senior engineers
avoid, and the team loses its most valuable production learning
channel.

## Related

- [Operational heroics](operational-heroics.md) - The anti-pattern this prevents
- [Postmortem anatomy](postmortem-anatomy.md) - Where incident findings become action items

---

Return to [SRE](_index.md)
