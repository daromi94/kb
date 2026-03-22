# Channels

A Channel is the core client-side abstraction that isolates the
application layer from the complexities of network transport,
connection pooling, and routing. It handles name resolution, load
balancing, connection management, and the interceptor pipeline. Client
stubs are created from a Channel.

## Responsibilities

**Name resolution:** Pluggable resolvers translate a target URI (DNS
name, service discovery endpoint) into a list of backend addresses.

**Load balancing:** A policy distributes RPCs across resolved
addresses. `pick_first` tries addresses in order and sends all RPCs
to the first one that connects. `round_robin` distributes across all
available backends.

**Subchannels:** Each resolved backend address gets a subchannel — a
logical abstraction that wraps connection management, connectivity
state, and reconnection logic for that address. A channel may be
backed by many HTTP/2 connections through its subchannels.

**Interceptors:** The channel is the entry point for client-side
interceptors, injecting cross-cutting concerns (auth tokens, tracing,
logging) into every RPC.

## State machine

| State             | Description                                   |
|-------------------|-----------------------------------------------|
| IDLE              | No connection. Transitions to CONNECTING on   |
|                   | first RPC.                                    |
| CONNECTING        | Establishing TCP, negotiating TLS, exchanging |
|                   | HTTP/2 settings.                              |
| READY             | Transport established. Multiplexing RPC       |
|                   | streams.                                      |
| TRANSIENT_FAILURE | Connection lost. Retries with exponential     |
|                   | backoff.                                      |
| SHUTDOWN          | Terminated by application. New RPCs fail      |
|                   | immediately. Pending RPCs continue until      |
|                   | cancelled.                                    |

## Lifecycle

Channels are thread-safe and designed to be long-lived. The standard
practice is to instantiate a single channel per target service during
application startup and share that instance across all concurrent
threads and requests. High-throughput scenarios may need a pool of
channels to the same target when hitting HTTP/2 concurrent stream
limits.

Creating a new channel per RPC is an antipattern: it bypasses HTTP/2
multiplexing, exhausts ephemeral ports, and degrades throughput.

---

Return to [gRPC](_index.md)
