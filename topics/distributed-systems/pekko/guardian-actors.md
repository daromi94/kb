# Guardian actors

Every actor system starts with two top-level guardians that form the
root of the actor tree. User-created actors are children of these
guardians — the entire system lifecycle is managed with the same
supervision and watching principles as any other actor.

## /user guardian

The entry point for application logic. All actors created via
`ActorSystem.spawn(...)` or `ActorContext.spawn(...)` are children of
this guardian.

Its role is to bootstrap the application by spawning top-level
subsystems. The ActorSystem's lifecycle is bound to this actor —
when the user guardian stops, the system initiates shutdown.

## /system guardian

Manages internal infrastructure (logging, cluster heartbeats) that
must remain operational while user actors are failing or shutting
down.

The system guardian watches the user guardian. It begins its own
termination only after /user has fully stopped, ensuring logging
stays available throughout the shutdown of application actors.

## Shutdown sequence

1. The /user guardian is signaled to stop and recursively terminates
   all its children
2. The /system guardian detects /user's termination via death watch
3. /system shuts down infrastructure actors (logging, etc.)
4. The ActorSystem terminates its threads

## Related

- [Supervision](supervision.md) - Parent-child fault handling
- [Hierarchical design](hierarchical-design.md) - Structuring actor hierarchies

---

Return to [Pekko](_index.md)
