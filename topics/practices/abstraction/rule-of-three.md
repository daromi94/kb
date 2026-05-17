# Rule of three

The Rule of Three is a heuristic for deciding when to abstract: do not
generalize a piece of logic until it has been implemented in three distinct
contexts. With three concrete examples, the true commonality becomes visible
and the abstraction can be shaped around what is actually shared rather than
what was imagined.

## The progression

1. **First instance:** Solve the problem directly. Write the simplest code
   that works.
2. **Second instance:** Notice the similarity. Resist the urge to abstract.
   Copy-paste is often cheaper than the wrong abstraction at this stage.
3. **Third instance:** The pattern is now undeniable. Identify what is truly
   common across all three cases and extract it.

## Building evolvable systems

The Rule of Three is part of a broader philosophy: aim for malleability over
up-front perfection. A system that can evolve is more valuable than one that
is "elegant" but rigid.

**Solve the specific problem first.** Avoid "what if" scenarios. Specific code
is easy to delete, easy to move, and easy to test.

**Let patterns emerge naturally.** Patterns are discovered, not dictated. By
waiting for a pattern to appear across multiple modules, the resulting
abstraction will be tighter and more accurate to actual needs.

**Refactor incrementally.** Rather than a large "day zero" design phase,
refactor as requirements become clearer. Abstractions crystallize naturally
from specific implementations.

---

Return to [Abstraction](_index.md)
