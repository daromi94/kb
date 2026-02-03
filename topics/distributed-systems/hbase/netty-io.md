# HBase Netty I/O

HBase 2.0+ uses Netty for event-driven I/O, replacing the legacy blocking
implementation. This enables higher throughput, lower latency, and better
resource management.

## RPC layer

The legacy implementation (`SimpleRpcServer`/`BlockingRpcClient`) required a
dedicated thread per connection, scaling poorly with thousands of concurrent
connections due to context switching overhead.

**NettyRpcClient:**

- Uses Netty's EventLoopGroup instead of blocking threads
- Small number of worker threads (default: `cpu_cores * 2`) handle I/O for
  thousands of connections
- Standard ChannelPipeline for Protobuf encoding/decoding, SASL authentication,
  and compression

**NettyRpcServer:**

- Accepts connections and hands packets to CallRunner
- Actual database logic still executes in a separate Handler thread pool to
  avoid blocking I/O threads

This decouples open connections from active threads—10,000 idle clients don't
require 10,000 waiting threads.

## AsyncFSWAL

The Write-Ahead Log is the primary write throughput bottleneck. The modern
implementation uses Netty for asynchronous HDFS writes.

**Legacy FSHLog:** Used a RingBuffer and blocking I/O streams.

**AsyncFSWAL architecture:**

```
+------------------+
|   Write Request  |
+--------+---------+
         |
         v
+--------+---------+
|   AsyncFSWAL     |
+--------+---------+
         |
  +----+----+----+
  |    |    |    |  Fan-out (parallel)
  v    v    v    v
+--+ +--+ +--+ +--+
|DN| |DN| |DN| |DN|  DataNodes via Netty
+--+ +--+ +--+ +--+
```

Instead of the standard HDFS pipeline (`A → B → C`), AsyncFSWAL opens direct
Netty connections to all DataNodes simultaneously. The write is considered
synced once all replicas acknowledge.

## Configuration

Key properties in `hbase-site.xml`:

| Property                    | Description                                   |
|-----------------------------|-----------------------------------------------|
| `hbase.rpc.client.impl`     | Set to `NettyRpcClient` to force Netty client |
| `hbase.wal.provider`        | Set to `asyncfs` for Netty-based WAL          |
| `hbase.netty.worker.count`  | EventLoopGroup thread count (tune for 10GbE+) |
| `hbase.netty.eventloop.rpc` | Channel type: `nio` (standard) or `epoll`     |

## Epoll optimization

On Linux, HBase can use Netty's native Epoll transport instead of Java NIO:

- Uses edge-triggered notifications
- Less garbage collection overhead
- Auto-detected if `netty-transport-native-epoll` is on the classpath

## Related

- [Storage engine](storage-engine.md) - Where AsyncFSWAL fits in the write path
- [Architecture](architecture.md) - RegionServer RPC handling
