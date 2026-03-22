# Heuristics vs. algorithms

Heuristics are provisional, plausible guidelines that require
judgment to apply. They are not mechanical operations that guarantee
an answer. Problem-solving cannot be reduced to a flawless,
automated process.

## The distinction

An algorithm terminates with a correct answer for every valid input.
A heuristic steers thought toward a solution but offers no such
guarantee. The value of a heuristic lies in narrowing the search
space — trading certainty for practical progress.

## Examples

| Heuristic       | Why it requires judgment                                |
|-----------------|---------------------------------------------------------|
| Design patterns | A Factory where a function suffices is over-engineering |
| SOLID, DRY      | No linter can verify true adherence — context decides   |
| A* search       | Trades optimal guarantee for tractable approximation    |

## Application questions

- Are you expecting a tool to resolve a design debate that actually
  requires human trade-offs?
- Is a strict rule blocking progress when it should be treated as
  a provisional guideline?
- Can an intractable problem be solved by accepting a good-enough
  approximation?

## Related

- [The four-phase method](four-phase-method.md) - Overarching process

---

Return to [Problem-solving](_index.md)
