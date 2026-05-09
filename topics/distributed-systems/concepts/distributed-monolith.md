# Distributed monolith

A distributed monolith is a system split into multiple deployable services
that retains the tight coupling of a single application. It suffers from
the drawbacks of both microservices (network latency, operational
complexity) and monoliths (no independent deployability, cascading
failures).

## How to detect it

- **Lock-step deployments.** Updating one service requires deploying
  several others simultaneously to avoid breakage.
- **Shared database.** Multiple services read and write the same tables.
  A schema change in one service immediately breaks others.
- **High network chatter.** A single user request triggers a long chain
  of synchronous calls between services, adding latency at every hop.
- **Cascading failures.** A timeout or failure in one service propagates
  upward through synchronous call chains, crashing the entire stack.
- **Cross-team coordination.** Every feature requires multiple teams to
  align on changes across service boundaries.

## Common causes

**Splitting by technical layer instead of business domain.** Separating
into "UI service", "business logic service", and "data access service"
creates services that cannot function independently.

**Entity services.** Designing services around individual database tables
forces constant synchronous communication for any meaningful operation.

**Premature fragmentation.** Breaking a system apart before domain
boundaries are understood locks in the wrong seams.

**Shared business-logic libraries.** When core rules live in a shared
library, every consumer must update in lockstep whenever a rule changes.

## How to fix it

**Bounded contexts.** Redefine service boundaries around business
capabilities. Group related behaviors and data into cohesive modules
rather than technical functions.

**Database per service.** Each service owns its data exclusively. Other
services access it through APIs or events, eliminating shared schema
coupling.

**Asynchronous communication.** Replace synchronous REST/RPC chains with
event-driven messaging. This removes temporal coupling — services do not
need each other to be online to function.

**Strangler fig pattern.** Build properly bounded services around the
edges of the existing system, incrementally routing traffic to them until
the old architecture can be decommissioned.

## Key lessons

**Complexity shifts, it does not disappear.** Moving to a distributed
system shifts complexity from in-memory calls to network communication
and distributed state. Wrong boundaries multiply the cost over a network.

**Monoliths are a valid starting point.** A well-structured modular
monolith is often safer than premature microservices. Refactoring tight
coupling within one codebase is far easier than refactoring chatty
network calls across repositories.

**Data dictates boundaries.** If services cannot be decoupled at the
database level, they cannot be decoupled at the deployment level.
Splitting compute without splitting data guarantees a distributed
monolith.

**Conway's Law is unavoidable.** Architecture mirrors organizational
communication structures. Teams organized by technical layer produce
systems that require cross-team coordination for every feature.

**Refactoring across a network is expensive.** Fixing an interface inside
one application is a method rename. Fixing an API between services
requires versioning, backward compatibility, and coordinated rollouts.

---

Return to [Concepts](_index.md)
