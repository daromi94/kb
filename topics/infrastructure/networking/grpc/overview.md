# Overview

gRPC is an RPC framework that uses Protocol Buffers as its IDL and
default serialization format. It runs over HTTP/2, giving it multiplexed
streams over a single TCP connection, binary framing, header compression,
and persistent connections.

## Contracts and code generation

Services are defined in `.proto` files with strongly typed message and
method definitions. The `protoc` compiler generates client stubs and
server base classes across languages (Go, Java, C++, Python, and
others), enforcing schema agreement between communicating services.

## Communication patterns

| Pattern                 | Client sends | Server sends |
|-------------------------|--------------|--------------|
| Unary                   | One message  | One message  |
| Server streaming        | One message  | Stream       |
| Client streaming        | Stream       | One message  |
| Bidirectional streaming | Stream       | Stream       |

**Unary RPC:** Standard request-response. One request, one response.

**Server streaming:** The client sends a single request and reads a
stream of messages back from the server.

**Client streaming:** The client writes a sequence of messages to the
server, which returns a single response after processing the stream.

**Bidirectional streaming:** Both sides send message sequences over
independent read-write streams. The two streams operate independently,
so each side reads and writes in whatever order it chooses.

---

Return to [gRPC](_index.md)
