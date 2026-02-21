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

## Key modules

| Module           | Purpose                                         |
|------------------|-------------------------------------------------|
| Actors           | Core actor system and typed actor API           |
| Streams          | Backpressured asynchronous stream processing    |
| Cluster          | Membership, sharding, and distributed data      |
| Persistence      | Event sourcing and durable state for actors     |
| HTTP             | HTTP server and client built on Streams         |
| gRPC             | gRPC server and client support                  |
| Cluster Sharding | Distribute actors across cluster by entity ID   |
| Connectors       | Integration with external systems (Kafka, etc.) |

## Related

- [Encapsulation and concurrency](encapsulation-and-concurrency.md) - The problem actors solve

---

Return to [Pekko](_index.md)
