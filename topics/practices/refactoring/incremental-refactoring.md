# Incremental Refactoring

Large-scale refactors are difficult to merge and harder to debug. Favor
incremental state transitions.

## Atomic commits

Small, verifiable changes limit the blast radius of logic errors. If a change
touches 50+ files, it's not a refactor—it's a liability.

| Commit size | Reviewability | Debuggability | Risk   |
|-------------|---------------|---------------|--------|
| 1-5 files   | High          | High          | Low    |
| 10-20 files | Medium        | Medium        | Medium |
| 50+ files   | Low           | Low           | High   |

## Change-verify-commit loop

Use a tight feedback loop:

1. Modify a single abstraction
2. Run the regression suite
3. Verify behavior is preserved
4. Commit

This keeps each change isolated and verifiable.

---

Return to [Refactoring](_index.md)
