# TCP Streams

TCP provides a **byte stream** abstraction with no concept of message
boundaries. This fundamental property affects how applications must handle
data.

## No Message Boundaries

Unlike UDP (discrete datagrams), TCP presents a continuous stream of bytes.

**The problem**: If you send "Hello" then "World":

```
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

```
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

## Framing: The Application's Job

Since TCP destroys message boundaries, applications must implement **framing**
to delimit messages.

**Common approaches:**

| Method        | Example               | Description             |
|---------------|-----------------------|-------------------------|
| Delimiter     | HTTP/1.1, Redis       | End message with `\r\n` |
| Length prefix | Most binary protocols | Send length, then data  |
| Fixed size    | Some legacy protocols | All messages same size  |

**Length prefix example:**

```
Sender:  [4 bytes: length=5][5 bytes: "Hello"]
Receiver: read 4 bytes → know to read 5 more → have complete message
```

## Nagle's Algorithm

By default, TCP buffers small writes to improve efficiency. If you write
single bytes rapidly, TCP waits briefly to batch them into one segment.

**Good for**: bulk transfer, reducing "tinygram" overhead

**Bad for**: interactive/real-time applications (SSH keystrokes, games)

**Disable with**: `TCP_NODELAY` socket option

## Related

- [TCP Segment](segment.md) - Actual packet structure
- [TCP Performance](performance.md) - Nagle and TCP_NODELAY details
