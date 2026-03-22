# Message ordering

gRPC guarantees strict message ordering within a single RPC call. If a
sender transmits messages M1, M2, M3, the receiver reads them in that
exact sequence. This holds for all streaming patterns: client streaming,
server streaming, and both directions of a bidirectional stream
independently.

## Mechanism

The guarantee is inherited from the transport stack, not implemented by
gRPC application logic:

1. TCP delivers an ordered, lossless byte stream.
2. HTTP/2 requires that frames belonging to a given stream ID are
   processed in the order received from the TCP socket.

Since gRPC maps one RPC to one HTTP/2 stream, protocol-level ordering
passes straight through to the unmarshalling layer.

## Boundaries

**Cross-stream:** No ordering exists between different RPC calls.
HTTP/2 frames from separate streams are multiplexed and interleaved on
the wire. The server may fully process stream B before stream A
regardless of initiation order.

**Network intermediaries:** L7 proxies and service meshes preserve
ordering within a proxied stream but may introduce varying latency
between different streams.

**Concurrent writes:** If multiple threads write to the same stream
without synchronization, the order messages reach the gRPC runtime is
non-deterministic. The stream transmits in the order it receives, but
that order is a race condition created by the application.

---

Return to [gRPC](_index.md)
