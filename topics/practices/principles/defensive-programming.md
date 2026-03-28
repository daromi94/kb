# Defensive programming

Write code that expects failure, validates assumptions, and degrades
gracefully rather than catastrophically. Every input is hostile, every
dependency will fail, every edge case will be hit in production.

## Validate at boundaries

The moment data crosses a trust boundary — API input, file read,
database result, IPC message — validate it. Check type, length, bounds,
and format. Reject malformed payloads immediately; attempting to
sanitize or guess intent introduces vulnerabilities. Never carry
untrusted data deep into the call stack.

## Fail fast

A loud crash at the source is far easier to debug than silent
corruption discovered three layers later. When execution reaches an
impossible or undefined state, halt or throw a descriptive exception
instantly. Deferred errors obscure root causes, complicate debugging,
and risk corrupting downstream processes.

Write error branches before the success path. It forces clarity about
what can go wrong and keeps the happy path clean. Check error codes,
null results, and empty collections — even from internal functions.

Use assertions to validate internal logic and conditions that should
be impossible. Assertions catch violated assumptions early and halt
execution before corrupt state propagates.

## Default to safety

Make the safe choice the obvious choice. Prefer explicit behavior over
defaults and implicit type coercion — make intent visible in code.

Access controls and logic branches should default to the safest state.
Switch statements must include a default case that throws for unhandled
values. Prefer whitelists over blacklists: blacklists are incomplete
by definition, while whitelists define exactly what is allowed.

## Favor immutability

Mutable state invites race conditions and unpredictable side effects.
Defaulting to immutable data structures enforces thread safety and
deterministic behavior across concurrent processes.

## Opaque error handling

Internal stack traces, memory addresses, and schema details must never
leak to external interfaces. Log exceptions internally with full
context; return sanitized, standardized fault codes to consumers.

## Design for partial failure

Services will be unavailable, responses will time out, and messages
will be duplicated. Idempotency ensures repeated requests produce the
same result, retries with exponential backoff avoid overwhelming a
recovering service, and circuit breakers stop calling a failing
dependency so it has time to recover. These are defensive tools, not
optional extras.

## Barricades

A barricade is the boundary where thorough validation happens.
Outside the barricade, data is untrusted and every input gets
checked rigorously — type, range, format, semantic validity.
Inside the barricade, code operates in a zone of relative trust
because everything crossing in has already been validated and
converted to a trusted internal representation.

This answers "how much checking is enough?" Protect heavily at
zone boundaries. Use assertions for internal invariants. Trust
validated data inside the zones. Concentrate protection where it
matters instead of spreading shallow checks everywhere.

The degenerate form — every function checking every input against
every possible invalid state — is counterproductive. Redundant
internal checks bloat the code, reduce signal-to-noise, and
paradoxically mask the absence of proper boundary checks. Every
check should exist because there is a specific scenario where it
prevents harm.

## Anti-patterns

**Swallowing errors silently.** Catching an exception and returning
a default value converts a detectable problem into an undetectable
one. The caller never knows something failed.

**Correcting bad data.** Silently truncating strings, clamping
numbers to valid ranges, or substituting defaults hides bugs in
calling code. The "corrected" data may be structurally valid but
semantically wrong — a truncated address, a clamped price at the
minimum instead of the intended value.

**Checking the wrong thing.** Validating that a string is non-empty
when the requirement is a valid email address. Checking that a
number is positive when the requirement is a product ID that exists
in the database. Surface-level checks create false security.

**Inconsistent protection.** Checking inputs rigorously in some
functions but not others based on intuition about what "could" go
wrong. The functions that seem safe become unsafe after a refactor
changes the assumptions.

## Log for reconstruction

When something breaks at 3am, the logs are the only witness. Capture
request identifiers, input values, the operation attempted, and the
error returned. The goal is a complete trace from trigger to failure
without reproducing the scenario.

---

Return to [Principles](_index.md)
