# Rewrite Fallacy

A total rewrite is rarely a technical optimization; it is usually a
manifestation of developer ego.

## Risk profile

| Code type   | Unknowns         |
|-------------|------------------|
| Legacy code | Known unknowns   |
| Rewrite     | Unknown unknowns |

## Knowledge loss

Deleting working code deletes the historical context of every production fire
that shaped it. If you can't explain *why* the code is bad in terms of Big O
complexity, coupling, or extensibility, you aren't ready to replace it.

## Readiness check

Before proposing a rewrite, articulate the problem in concrete terms:

- What is the specific performance bottleneck?
- Which coupling makes changes difficult?
- What extensibility is blocked?

If the answer is "it's ugly" or "I don't understand it," that's not sufficient
justification.

---

Return to [Refactoring](_index.md)
