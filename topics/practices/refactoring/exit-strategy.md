# Exit strategy

Refactoring is a hypothesis that the new architecture will be superior. Like any
hypothesis, it can be disproven.

## When to abort

If mid-sprint the complexity of the refactor begins to eclipse the value of the
original implementation, you must be prepared to abort.

| Signal                             | Action          |
|------------------------------------|-----------------|
| Scope keeps expanding              | Re-evaluate     |
| Discovering more hidden invariants | Consider abort  |
| Breaking unrelated tests           | Abort           |
| Timeline exceeds original estimate | Re-evaluate ROI |

## Failed refactor vs shipped regression

A failed refactor that ends in `git reset --hard` is a better outcome than a
"completed" refactor that introduces intermittent production outages.

The sunk cost of time invested is not a valid reason to ship risky code.

---

Return to [Refactoring](_index.md)
