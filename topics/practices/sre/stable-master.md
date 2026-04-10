# Stable master

The main branch is always deployable. Pull the latest code from main at
any moment, and it compiles, passes all tests, and is safe to ship to
production. This is not a branching strategy — it is a quality
invariant applied to the main branch.

## Gated integration

Developers do not commit directly to main. Work happens on feature
branches that must pass CI, code review, and sometimes a staging soak
before merging. Feature branches can live for hours, days, or
occasionally weeks. The common thread across variants like GitHub Flow
and GitFlow is that merging into the mainline is a gated event — code
earns its way in.

## Keeping the build green

A stable main is only as good as the mechanisms that protect it:

| Mechanism           | Purpose                                    |
|---------------------|--------------------------------------------|
| Pre-merge CI gates  | Block merges that fail tests or linting    |
| Code review         | Catch logic and design issues before merge |
| Automated rollbacks | Revert failed deployments to last stable   |

If a bad commit slips through and breaks the build, the team treats it
as a stop-the-line event: all feature work pauses until main is green
again. A broken main blocks every developer who depends on it, so fast
recovery is non-negotiable.

## Tradeoffs

Integration is deferred until a feature is "ready." This keeps the
mainline clean but risks painful merges, long feedback loops, and
integration drift when branches live too long.

## Related

- [Trunk-based development](trunk-based-development.md) - Complementary integration workflow

---

Return to [SRE](_index.md)
