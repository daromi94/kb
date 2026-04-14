# Crash or continue

When a server hits an unexpected error, it faces a binary choice: kill the
whole process, or drop the current task and stay alive. The right answer is
not a property of the line of code that failed — it is a property of the
architecture the code runs inside. Crashing on the same error is correct
in one service and catastrophic in another.

Three questions decide.

## 1. Are the failures correlated?

Crashing is only safe when other healthy servers will not hit the same
error.

**Uncorrelated — crash.** Uncorrectable memory faults, dead disks, kernel
panics. Random hardware events do not propagate to healthy peers, so
taking the bad node out of service is clean.

**Correlated — stay alive.** A null pointer triggered by a specific
customer payload is not random; it is deterministic. If the server
crashes, the load balancer routes the same poison pill to the next node,
then the next, until the entire fleet is offline. Drop the request,
return a 5xx, and keep serving everyone else.

## 2. Can the error be handled at a higher layer?

Crashing is cheap or expensive depending on what replaces the dead
component.

**Minutes to replace.** A monolithic web server takes seconds or minutes
to boot. Crashing is disruptive; in-process recovery is preferable.

**Milliseconds to replace.** Erlang actors and serverless function
invocations are designed for high rates of short-lived component deaths,
and a supervisor reconstitutes them instantly. Crashing is cleaner than
in-process recovery.

"Let it crash" works because the supervision tree makes a crashing
component the expected, cheap case — not because crashing is inherently
virtuous.

## 3. Is it possible to meaningfully continue?

Some errors make continuation unsafe in a way no engineering can repair
later.

**Safe to continue — configuration.** A malformed global config file
should not take the server down. Keep the last-known-good config, alert
operators, and continue serving traffic on slightly stale settings.

**Unsafe to continue — state and data.** A database replica that
receives a replication record it does not understand must crash.
Skipping the record would silently corrupt state and return wildly
wrong answers to clients. In databases, correctness is non-negotiable.

The config/state distinction generalizes: if continuing risks incorrect
data or violated durability, crash. If it just means running on slightly
stale inputs, keep going.

## Scenarios

| Scenario                         | Correlation  | Replace time | Continuation | Decision     |
|----------------------------------|--------------|--------------|--------------|--------------|
| Uncorrectable RAM fault          | Uncorrelated | —            | —            | Crash        |
| Null pointer on specific payload | Correlated   | —            | —            | Drop request |
| Bad replication record           | —            | —            | Unsafe       | Crash        |
| Malformed global config file     | —            | —            | Safe         | Continue     |
| Serverless function on bad input | —            | Instant      | —            | Crash        |
| Monolithic server with live bug  | —            | Minutes      | —            | Stay alive   |

## Related

- [Blast radius reduction](blast-radius-reduction.md) - Mitigation when
  the decision is wrong

---

Return to [Concepts](_index.md)
