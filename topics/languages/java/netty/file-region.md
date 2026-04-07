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

**SSL/TLS defeats it.** Encryption requires reading bytes into
userspace for transformation. When an SslHandler is in the pipeline,
FileRegion cannot be used. The fallback for encrypted connections is
ChunkedWriteHandler with ChunkedFile or ChunkedNioFile, which
streams the file in fixed-size pieces to avoid loading the entire
file into memory.

**Transforming handlers defeat it.** Compression, chunked transfer
encoding, checksum computation — any outbound handler that needs to
see the bytes forces a read-into-buffer fallback. A FileRegion
written into a pipeline with an HttpContentCompressor silently
degrades to standard I/O.

**FileRegion is not a ByteBuf.** It is a separate type in the
outbound path. Handlers that only know about ByteBuf pass it through
unchanged (usually correct) or fail on an unchecked cast. Outbound
handlers between the file source and the socket must either pass
FileRegion through or explicitly convert it.

## Related

- [Zero copy](zero-copy.md) - Application-level techniques and the pipeline principle
- [Transport](transport.md) - Pluggable I/O mechanisms

---

Return to [Netty](_index.md)
