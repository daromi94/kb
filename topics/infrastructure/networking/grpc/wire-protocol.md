# Wire protocol

gRPC maps each RPC onto HTTP/2 primitives with a defined frame
sequence. One RPC corresponds to one HTTP/2 stream.

## Request

The client opens a stream with a HEADERS frame containing:

| Header         | Value                                            |
|----------------|--------------------------------------------------|
| `:method`      | `POST`                                           |
| `:path`        | `/{package}.{ServiceName}/{MethodName}`          |
| `:scheme`      | `http` / `https`                                 |
| `content-type` | `application/grpc` (optionally `+proto`/`+json`) |
| `te`           | `trailers`                                       |

Custom application metadata is sent as additional headers.

## Length-prefixed framing

Before entering HTTP/2 DATA frames, every message is wrapped in a
5-byte prefix:

```text
+-----------+----------------+-----------------------+
| Comp (1B) | Length (4B BE) | Protobuf payload ...  |
+-----------+----------------+-----------------------+
```

**Compressed-Flag:** 0 or 1 (1 byte). Indicates whether the payload
is compressed.

**Message-Length:** Payload size in bytes (4 bytes, big-endian unsigned
integer).

DATA frame boundaries have no relation to length-prefixed message
boundaries — a single message may span multiple DATA frames.

## Response and trailers

The server sends its own HEADERS frame (initial metadata), followed by
DATA frames carrying length-prefixed response messages.

The call closes with a trailing HEADERS frame (HTTP/2 trailers)
carrying:

| Trailer        | Required | Value                             |
|----------------|----------|-----------------------------------|
| `grpc-status`  | Yes      | Status code (e.g., `0` = OK)      |
| `grpc-message` | No       | Percent-encoded error description |

The client runtime parses these trailers to return the result or raise
an error.

---

Return to [gRPC](_index.md)
