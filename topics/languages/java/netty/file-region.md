# File region

FileRegion enables OS-level zero-copy file transfer. Bytes move from
the filesystem page cache to the network socket inside the kernel,
bypassing userspace entirely. The CPU never touches the payload —
DMA handles the transfer.

## How it works

DefaultFileRegion wraps a FileChannel and delegates to
`FileChannel.transferTo()`, which on Linux maps to `sendfile(2)`.
Traditional file transfer requires four context switches and four
memory copies (disk to kernel read buffer to userspace to kernel
socket buffer to NIC). With sendfile, data moves from the page cache
directly to the socket buffer in two context switches.

```java
@Override
protected void channelRead0(ChannelHandlerContext ctx, FileRequest req) throws Exception {
    RandomAccessFile raf = new RandomAccessFile(req.file(), "r");
    FileRegion region = new DefaultFileRegion(raf.getChannel(), 0, raf.length());
    ctx.writeAndFlush(region).addListener(f -> raf.close());
}
```

## Constraints

Any handler that touches the bytes kills the zero-copy path:

- **SSL/TLS** — encryption must happen in userspace. When an
  SslHandler is in the pipeline, use ChunkedWriteHandler with
  ChunkedFile instead, which streams the file in fixed-size pieces.
- **Compression and checksums** — any transforming outbound handler
  forces a read-into-buffer fallback. An HttpContentCompressor in
  the pipeline silently degrades FileRegion to standard I/O.
- **Type mismatch** — FileRegion is not a ByteBuf. Outbound handlers
  between the file source and the socket must pass it through or
  explicitly convert it; an unchecked cast to ByteBuf will fail.

---

Return to [Netty](_index.md)
