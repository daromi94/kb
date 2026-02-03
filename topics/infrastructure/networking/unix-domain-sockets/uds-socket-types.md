# UDS Socket Types

Unix Domain Sockets support three socket types, each with different semantics
for connection state and message boundaries.

## SOCK_STREAM

The TCP equivalent. Connection-oriented with byte-stream semantics.

```c
int fd = socket(AF_UNIX, SOCK_STREAM, 0);
```

**Characteristics:**

- Requires `connect()` before sending
- No message boundaries (bytes flow like water from a tap)
- Application must parse where messages begin and end

**Message boundary problem:**

```
Sender:  write("Hello") then write("World")
Receiver: might read "HelloWorld" in one chunk
```

## SOCK_DGRAM

The UDP equivalent, but with critical differences.

```c
int fd = socket(AF_UNIX, SOCK_DGRAM, 0);
```

| Aspect      | Network UDP      | UDS Datagram              |
|-------------|------------------|---------------------------|
| Connection  | Not required     | Not required              |
| Reliability | Packets can drop | **Reliable** (kernel RAM) |
| Ordering    | Can reorder      | **Ordered**               |
| Boundaries  | Preserved        | Preserved                 |

**Use case:** Logging (syslog), simple event notifications where you want
message boundaries without connection overhead.

## SOCK_SEQPACKET

The best of both worlds. Connection-oriented with preserved message boundaries.

```c
int fd = socket(AF_UNIX, SOCK_SEQPACKET, 0);
```

**Characteristics:**

- Requires `connect()` (like STREAM)
- Message boundaries preserved (like DGRAM)
- One `write()` = one `read()` guaranteed

**Use case:** Protocols needing sessions and discrete messages without manual
parsing.

## Flow Control

Unlike TCP's sliding window with ACKs, UDS uses kernel buffer locking:

1. Each socket has a receive buffer limit (`net.core.rmem_default`)
2. If sender fills receiver's buffer, kernel blocks the `write()` call
3. Sender sleeps until receiver reads and frees space
4. Kernel wakes sender to continue

Zero protocol overhead for backpressure.

## Summary

| Type           | Connection | Boundaries | Analogy            |
|----------------|------------|------------|--------------------|
| SOCK_STREAM    | Yes        | None       | TCP                |
| SOCK_DGRAM     | No         | Preserved  | UDP (but reliable) |
| SOCK_SEQPACKET | Yes        | Preserved  | SCTP               |

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [UDS lifecycle](uds-lifecycle.md) - API flow for each type
