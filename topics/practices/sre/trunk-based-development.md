# Trunk-based development

Trunk-based development (TBD) is a branching model where every
developer commits to a single shared branch — the trunk — at least
daily, usually many times a day. The goal is to eliminate the pain of
long-lived branches: merge conflicts, integration drift, and
"big bang" merges.

## How it works

Branches, if they exist at all, are extremely short-lived (hours, not
days) and exist only to run CI before merging. Because commits land on
trunk constantly, unfinished work is hidden behind **feature flags**
rather than isolated on branches.

Releases are cut directly from trunk or from short-lived release
branches that only receive cherry-picked fixes. Feature flags decouple
deployment from release — code ships to production continuously, but
incomplete features stay invisible to users until the flag is turned on.

## Requirements

TBD demands more from engineering infrastructure than branch-based
workflows:

| Requirement      | Why                                          |
|------------------|----------------------------------------------|
| Strong CI        | Every commit hits trunk; breakage is instant |
| Fast test suites | Slow tests bottleneck the merge queue        |
| Feature flags    | Hide incomplete work without branches        |
| Small commits    | Easier to review, test, and revert           |
| Stable trunk     | Broken trunk blocks every developer          |

## Tradeoffs

Pays integration cost continuously in tiny increments rather than
deferring it. Dramatically shortens feedback loops and is a
prerequisite for continuous delivery. Large-scale monorepos
(Google, Meta) run on this model.

The overhead is operational: teams need mature CI, flag management, and
the discipline to keep commits small and trunk green.

## Related

- [Stable master](stable-master.md) - The quality invariant TBD depends on

---

Return to [SRE](_index.md)
