# HTTP/2 transport

gRPC builds on HTTP/2's binary, multiplexed transport model. Each
HTTP/2 feature maps directly to an RPC capability.

## Multiplexing

HTTP/1.1 suffers from head-of-line (HoL) blocking: although pipelining
allows sending multiple requests without waiting, responses must return
in order, so a slow response stalls everything behind it. In practice,
clients open many TCP connections to get concurrency.

HTTP/2 interleaves frames from multiple independent streams over a
single persistent TCP connection. This eliminates HoL blocking at the
HTTP layer and avoids repeated TCP handshakes and TLS negotiations.
Client-initiated streams use odd-numbered IDs, server-pushed streams
use even IDs, and stream 0 is reserved for connection-level frames
such as `SETTINGS` and `PING`.

TCP-layer HoL blocking remains: a single lost packet stalls all streams
until retransmission completes, since TCP delivers an ordered byte
stream. This is a key motivation for QUIC/HTTP/3.

## Binary framing

All communication is encapsulated in binary frames (`HEADERS`, `DATA`,
`RST_STREAM`, `WINDOW_UPDATE`, and others). A stream opens when its
first `HEADERS` frame is sent and half-closes when either endpoint
marks a frame with the `END_STREAM` flag. Binary framing eliminates
the text parsing HTTP/1.1 requires — newlines, whitespace, chunked
encoding — and pairs end-to-end with Protocol Buffers: metadata rides
compressed in `HEADERS` via HPACK, and `DATA` frames carry payloads
that are already binary. Nothing is converted between text and binary
on the wire.

## Streaming

Each HTTP/2 stream is full-duplex at the framing layer: client and
server send `DATA` frames independently without waiting for each
other. gRPC maps one RPC to one stream, so a single call can carry
concurrent message flows in both directions. This is what makes
client streaming, server streaming, and bidirectional streaming
possible without workarounds like WebSockets or long-polling.

Each RPC pattern uses the stream differently:

| Pattern          | Client DATA | Server DATA |
|------------------|-------------|-------------|
| Unary            | One frame   | One frame   |
| Server streaming | One frame   | Many frames |
| Client streaming | Many frames | One frame   |
| Bidirectional    | Many frames | Many frames |

Every response ends with a trailing `HEADERS` frame carrying
`grpc-status`, even on success. This is an HTTP/2 `HEADERS` frame with
`END_STREAM` set, not HTTP/1.1-style chunked trailers.

## HPACK header compression

RPCs often carry repetitive metadata (auth tokens, content types,
tracing context). HTTP/2 compresses headers with HPACK, which combines
a static table of common headers, a dynamic table of previously sent
headers maintained by both endpoints, and Huffman coding for literal
values. This cuts bandwidth for high-volume, small-payload calls.

## Flow control

HTTP/2 provides credit-based flow control at two levels — per-stream
and per-connection — via `WINDOW_UPDATE` frames. A fast sender cannot
overwhelm a slow receiver or exhaust its memory buffers. Only `DATA`
frames are flow-controlled; control frames are not.

---

Return to [gRPC](_index.md)
