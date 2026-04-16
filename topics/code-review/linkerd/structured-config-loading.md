# Structured config loading

Treat configuration as a typed, validated tree that is parsed once at
startup, consumed by subsystem builders, and then discarded. The config
struct exists only long enough to prove the system can start correctly.

## How Linkerd2-proxy does it

Configuration is a nested struct tree that mirrors the subsystem
hierarchy — each subsystem owns its own typed config. The config
source is abstracted so parsing works against any backend, not just
environment variables. Validation has two layers: per-field type
parsing and cross-field semantic checks. If anything fails, the proxy
exits immediately — it never starts in a degraded state. At build
time, the config is destructured into subsystem builders and ceases
to exist. There is no runtime config reload.

## Why it works

A typed tree catches misconfiguration at the earliest possible moment
rather than at runtime. Failing fast is the right posture for a
container — a crash triggers a restart and the error is visible in
logs, while silent degradation from partial config is harder to
diagnose. Consuming the config once eliminates stale reads, config
drift, and partial reload bugs.

## Takeaway

The alternative — stringly-typed config read lazily at arbitrary
points — trades startup confidence for runtime surprises. When you
make the config ephemeral, you force every subsystem to declare its
requirements upfront. Nothing can silently depend on a value that was
never validated.

## Related

- [Cooperative drain shutdown](cooperative-drain-shutdown.md) - Shutdown discipline
- [Isolated admin server](isolated-admin-server.md) - Runtime operational interface

---

Return to [Linkerd2-proxy](_index.md)
