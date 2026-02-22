# Overview

Pekko is an actor-based toolkit for building concurrent, distributed,
and resilient systems on the JVM. It is an open-source fork of Akka,
maintained by the Apache Software Foundation.

## Core programming model

Actors are the fundamental unit of computation. Each actor:

- Encapsulates private state with no shared mutable data
- Processes one message at a time from its mailbox
- Communicates exclusively through asynchronous message passing
- Can create child actors, forming supervision hierarchies

This model eliminates locks and low-level concurrency primitives. The
same code works transparently across local and remote boundaries.

## Design mental model

Think of actors as people in an organization. Assign sub-tasks to
them, arrange their roles into a hierarchy, and define how failures
escalate. This maps directly to supervision trees, message protocols,
and task delegation in code.

## Key modules

| Module            | Purpose                                           |
|-------------------|---------------------------------------------------|
| Actors            | Core typed actor system and message passing       |
| Remoting          | Transparent message exchange across machines      |
| Cluster           | Membership protocol for coordinated actor systems |
| Cluster Sharding  | Distribute stateful actors across cluster nodes   |
| Cluster Singleton | Single service instance across the cluster        |
| Persistence       | Event sourcing and state recovery for actors      |
| Projections       | Consume event streams for views or downstream     |
| Distributed Data  | CRDTs for eventually consistent shared state      |
| Streams           | Backpressured async stream processing             |
| HTTP              | HTTP server and client built on Streams           |
| gRPC              | gRPC with protobuf integration                    |
| Connectors        | Infrastructure integrations (Kafka, etc.)         |

## Related

- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - The problem actors solve

---

Return to [Pekko](_index.md)
