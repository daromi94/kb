# Streams

TCP provides a **byte stream** abstraction with no concept of message
boundaries. This fundamental property affects how applications must handle
data.

## No message boundaries

Unlike UDP (discrete datagrams), TCP presents a continuous stream of bytes.

**The problem**: If you send "Hello" then "World":

```text
Sender:  write("Hello")  write("World")
```

The receiver might see:

- `"HelloWorld"` - messages merged (Nagle's algorithm bundled them)
- `"Hell"` then `"oWorld"` - split at arbitrary point
- `"Hello"` then `"World"` - lucky alignment (don't count on it)

TCP guarantees bytes arrive **in order**, but not **grouped as sent**.

## Segmentation

Large writes are chopped into segments fitting the MSS (Maximum Segment Size,
typically ~1460 bytes based on MTU).

```text
Application: write(1GB)
    ↓
TCP: chop into ~700,000 segments
    ↓
Network: transmit segments
    ↓
Receiver TCP: reassemble in buffer
    ↓
Application: read() sees continuous stream
```

The receiver never knows or cares about segment boundaries.

## Framing: the application's job

Since TCP destroys message boundaries, applications must implement **framing**
to delimit messages.

**Common approaches:**

| Method        | Example               | Description             |
|---------------|-----------------------|-------------------------|
| Delimiter     | HTTP/1.1, Redis       | End message with `\r\n` |
| Length prefix | Most binary protocols | Send length, then data  |
| Fixed size    | Some legacy protocols | All messages same size  |

**Length prefix example:**

```text
Sender:  [4 bytes: length=5][5 bytes: "Hello"]
Receiver: read 4 bytes → know to read 5 more → have complete message
```

## Nagle's algorithm

By default, TCP buffers small writes to improve efficiency. If you write
single bytes rapidly, TCP waits briefly to batch them into one segment.

**Good for**: bulk transfer, reducing "tinygram" overhead

**Bad for**: interactive/real-time applications (SSH keystrokes, games)

**Disable with**: `TCP_NODELAY` socket option

## Related

- [Segment structure](segment.md) - Actual packet structure
- [Performance](performance.md) - Nagle and TCP_NODELAY details

---

Return to [TCP](_index.md)
