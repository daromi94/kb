# Channels

A channel represents a virtual connection to a logical target, not a
single TCP connection. It is analogous to a database connection pool:
the application talks to one channel, and the channel manages a set
of subchannels to resolved backend addresses underneath. Client stubs
are created from a channel.

A channel handles name resolution, load balancing, connection
management, and the interceptor pipeline — isolating application code
from network transport.

## Responsibilities

**Name resolution:** Pluggable resolvers translate a target URI (DNS
name, service discovery endpoint) into a list of backend addresses.

**Load balancing:** A policy distributes RPCs across resolved
addresses. `pick_first` tries addresses in order and sends all RPCs
to the first one that connects. `round_robin` distributes across all
available backends.

**Subchannels:** The channel creates one subchannel per resolved
backend address. Each subchannel manages the HTTP/2 connection to a
specific IP:port and runs its own connectivity state machine
independently — if one backend goes down, only its subchannel retries
while the others keep serving.

```text
Channel (logical target)
  └─ Load Balancer
       ├─ Subchannel A (10.0.0.1:443) ── HTTP/2 conn
       ├─ Subchannel B (10.0.0.2:443) ── HTTP/2 conn
       └─ Subchannel C (10.0.0.3:443) ── HTTP/2 conn
```

The load balancer picks which subchannel receives each RPC. The
channel's own state derives from its subchannels — READY if any
subchannel is READY, TRANSIENT_FAILURE if all are.

**Interceptors:** The channel is the entry point for client-side
interceptors, injecting cross-cutting concerns (auth tokens, tracing,
logging) into every RPC.

## State machine

| State             | Description                                        |
|-------------------|----------------------------------------------------|
| IDLE              | No connection yet. Connects on first RPC.          |
| CONNECTING        | Establishing TCP + TLS + HTTP/2 settings.          |
| READY             | Transport up. Multiplexing RPC streams.            |
| TRANSIENT_FAILURE | Connection lost. Retries with exponential backoff. |
| SHUTDOWN          | New RPCs rejected. Pending RPCs continue.          |

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
