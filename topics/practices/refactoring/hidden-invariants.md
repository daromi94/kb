# Hidden invariants

Legacy code often contains hidden invariants—logic that must remain true even if
the implementation looks suboptimal. Before opening a PR, perform a behavioral
analysis.

## Chesterton's fence

If a piece of logic looks redundant or "weird," it is likely a patch for a
specific environment quirk or a race condition. That 500-line method with high
cyclomatic complexity? It's often a collection of undocumented bug fixes and
edge-case handling that has achieved production stability.

## Behavioral signature

Map the inputs and outputs of the module. Your goal is to change the
**structure** while maintaining an identical **behavioral signature**.

| Change type | Safe | Risky                          |
|-------------|------|--------------------------------|
| Structure   | Yes  | Only if it affects behavior    |
| Behavior    | No   | Violates the implicit contract |

---

Return to [Refactoring](_index.md)
