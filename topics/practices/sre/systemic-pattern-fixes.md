# Systemic pattern fixes

The most powerful use of a correction of errors (COE) database is
finding patterns across dozens of unrelated incidents. Individual
postmortems fix individual bugs. The outer loop fixes whole classes
of error.

## Clusters reveal structural problems

If multiple teams repeatedly fail at the same hard problem — for
example, managing database locks when clients disconnect — the answer
is not "be more careful." Relying on individual vigilance for a class
of bug is how that class of bug keeps shipping. The failures are a
signal that the abstraction the teams are working against is wrong.

## Build a primitive that makes the error impossible

Cluster the failures, then build a library, service, or architectural
primitive that makes the mistake structurally impossible. A new
lock-manager abstraction eliminates the lock bugs. A standardized
retry client eliminates the retry-storm bugs. The cost of the
primitive is paid once. The cost of the recurring bug compounds
forever.

The COE database is not just a log of what broke. It is the input to
the team's strategic resilience roadmap.

## Related

- [Postmortem anatomy](postmortem-anatomy.md) - The input data
- [Operational heroics](operational-heroics.md) - What this replaces

---

Return to [SRE](_index.md)
