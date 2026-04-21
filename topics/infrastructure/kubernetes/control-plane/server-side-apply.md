# Server-Side Apply

Server-Side Apply (SSA) is how the API server handles declarative
updates when multiple actors manage the same object. It tracks
which actor owns which field, and any write that would silently
overwrite another owner is rejected until the caller resolves the
conflict explicitly.

## Managers and managedFields

Every caller that applies changes identifies itself with a
**manager** name, via the `fieldManager` query parameter. On every
apply, the API server updates `metadata.managedFields` — a list of
entries recording which manager owns which fields and whether the
operation was `Apply` (declarative) or `Update` (imperative).

Ownership is tracked per field, not per object. Two managers can
edit the same object as long as they touch different fields.

## Conflicts and the three resolutions

A conflict occurs when manager B's apply tries to change a field
already owned by manager A. The API server rejects the request by
default, forcing B to make an explicit choice:

1. **Force override** (`kubectl apply --force-conflicts`) — B's
   value wins and A is dropped from ownership of that field.
2. **Give up** — remove the field from B's manifest. A's value
   stays, and B no longer claims the field.
3. **Share** — update B's local manifest to match the server's
   current value, then reapply. Both A and B are recorded as joint
   owners.

## Related

- [API server](api-server.md) - SSA runs during the persist stage

---

Return to [Control plane](_index.md)
