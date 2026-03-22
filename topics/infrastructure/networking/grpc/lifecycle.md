# RPC lifecycle

Every gRPC call follows a defined sequence of metadata and message
exchanges between client and server.

## Unary call flow

1. Client calls a stub method. The server receives client metadata,
   the method name, and the deadline.
2. Server may send its own initial metadata immediately or wait for
   the client's request message first. Either way, initial metadata
   must precede any response data.
3. Server processes the request and returns a response with status
   details and optional trailing metadata.
4. Client receives the response, completing the call.

## Streaming variations

**Server streaming:** Same as unary, but the server sends a stream of
messages instead of one response. Status details and trailing metadata
follow after all messages are sent.

**Client streaming:** The client sends a stream of messages. The server
responds with a single message, typically after receiving all client
messages — but it may respond earlier.

**Bidirectional streaming:** The client initiates; the server receives
metadata, method name, and deadline. The two streams are independent,
so each side reads and writes in any order. A server might wait for
all client messages, or the two sides might exchange messages in a
ping-pong fashion.

## Metadata

Metadata is per-call information carried as key-value pairs. Keys are
strings; values are strings or binary data.

Key naming rules:

- Case-insensitive
- ASCII letters, digits, `-`, `_`, `.`
- Keys starting with `grpc-` are reserved
- Binary-valued keys must end in `-bin`

gRPC does not interpret user-defined metadata. It exists for clients
and servers to pass out-of-band information (auth tokens, tracing
context) alongside calls.

---

Return to [gRPC](_index.md)
