# Remote Procedure Call

**RPC (Remote Procedure Call)** is a protocol that allows a program to execute a
function on a different computer as if it were a local call. The developer calls
`getUserData(id)` and the RPC framework handles the network communication behind
the scenes.

## Anatomy of an RPC

RPC uses two messengers called **stubs** to make remote calls appear local:

- **Client Stub:** A proxy on the client side with the same interface as the
  real function but containing only code to package the request
- **Server Stub (Skeleton):** The counterpart that receives the message,
  unpacks it, and calls the actual function on the server

## Workflow

When you call a remote function, these steps happen in milliseconds:

```
+--------+     +-------------+                    +-------------+     +--------+
| Client |---->| Client Stub |---- Network ------>| Server Stub |---->| Server |
|  App   |     |  marshall   |    (TCP/UDP)       |  unmarshall |     |  Func  |
+--------+     +-------------+                    +-------------+     +--------+
    ^                                                                      |
    |                         <- return result <-                          |
    +----------------------------------------------------------------------+
```

1. **Call:** Client application calls the client stub normally
2. **Marshalling:** Stub converts arguments to binary format (JSON, Protobuf)
3. **Transmission:** OS sends message over TCP or UDP
4. **Unmarshalling:** Server stub converts back to objects the server
   understands
5. **Execution:** Server performs the task
6. **Return:** Result marshalled, sent back, unmarshalled, returned to client

## RPC vs REST

| Feature     | RPC                                     | REST                               |
|-------------|-----------------------------------------|------------------------------------|
| Focus       | Actions: "Do this" (`sendMessage()`)    | Resources: "Get this" (`GET /m/1`) |
| Coupling    | Tight (strict contract/schema)          | Loose (URL + data format)          |
| Performance | Often faster (binary formats like gRPC) | Slower (text-heavy JSON/HTTP)      |

## Common Implementations

- **gRPC:** Google's high-performance framework, widely used in microservices
- **NFS:** Network File System uses RPC to make remote files feel local
- **Java RMI:** Java-specific RPC for communication between JVMs

## The Cost of Transparency

The danger of RPC is that it *looks* like a local call, causing developers to
forget the network exists:

- **Latency:** Local calls take nanoseconds; network calls take milliseconds
- **Partial Failure:** In local calls, either everything works or it crashes. In
  RPC, the server might complete the task but the network could fail before the
  success message reaches you

## Related

- [Client-Server](client-server.md) - The architecture RPC operates within
