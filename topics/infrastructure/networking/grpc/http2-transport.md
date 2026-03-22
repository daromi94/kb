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

TCP-layer HoL blocking remains: a single lost packet stalls all streams
until retransmission completes, since TCP delivers an ordered byte
stream. This is a key motivation for QUIC/HTTP/3.

## Binary framing

All communication is encapsulated in binary frames (`HEADERS`, `DATA`,
`RST_STREAM`, and others). This eliminates the text parsing that
HTTP/1.1 requires (newlines, whitespace, chunked encoding) and pairs
naturally with binary IDLs like Protocol Buffers.

## Streaming

Each HTTP/2 stream is full-duplex at the framing layer: client and
server send `DATA` frames independently without waiting for each other.
gRPC maps one RPC to one stream, so a single call can carry concurrent
message flows in both directions. This is what makes client streaming,
server streaming, and bidirectional streaming possible without
workarounds like WebSockets or long-polling.

## HPACK header compression

RPCs often carry repetitive metadata (auth tokens, content types,
tracing context). HTTP/2 compresses headers with HPACK, which combines
Huffman coding with an indexed table of previously sent headers
maintained by both endpoints. This reduces bandwidth for high-volume,
small-payload calls.

## Flow control

HTTP/2 provides credit-based flow control at two levels — per-stream
and per-connection — via `WINDOW_UPDATE` frames. A fast sender cannot
overwhelm a slow receiver or exhaust its memory buffers. Only `DATA`
frames are flow-controlled; control frames are not.

---

Return to [gRPC](_index.md)
