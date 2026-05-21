# Structured config loading

Treat configuration as a typed, validated tree: parse it once at
startup, hand it to subsystem builders, then discard it. The config
exists only long enough to prove the system can start correctly.

## The config lifecycle

Configuration is a typed tree that mirrors the subsystem hierarchy.
The config source is pluggable, so parsing works against any backend,
not just environment variables. Validation has two layers: per-field
type parsing and cross-field semantic checks. If anything fails, the
proxy exits immediately — it never starts in a degraded state.
Otherwise, subsystem builders consume the config, and it ceases to
exist. The proxy never reloads config at runtime.

## The payoff

A typed tree catches misconfiguration at startup, not at runtime.
Failing fast suits a container — a crash triggers a restart and the
error is visible in the logs, whereas silent degradation from partial
config is harder to diagnose. Consuming the config once eliminates
stale reads, drift, and partial-reload bugs.

## The forcing function

The alternative — untyped config read lazily at arbitrary points —
trades startup confidence for runtime surprises. Making the config
ephemeral forces every subsystem to declare its requirements upfront.
Nothing can silently depend on an unvalidated value.

---

Return to [Linkerd2-proxy](_index.md)
