# Backpressure

Trino's stages run at different speeds — a Parquet scan can produce
pages much faster than a complex aggregation can consume them. Without
flow control, the fast stage would race ahead, fill memory with pages
the slow stage cannot read, and crash the JVM. Backpressure is the
mechanism that makes the fast stage slow down to match the slow one,
without any central coordination.

## How it works

Between every pair of stages sits a memory-bounded buffer. The upstream
task writes finished pages into its output buffer; the downstream
worker runs an exchange client that pulls pages over HTTP. Both
buffers have a hard size cap.

When a buffer fills, the next driver attempting to write sees a
"buffer full" signal. Instead of blocking its OS thread, the driver
yields its time slice and goes BLOCKED. The thread is freed for any
other ready driver. The upstream operator pipeline stops pulling new
data, and the connector at the bottom (an S3 reader, a JDBC fetcher)
stops reading from its source.

The exchange client at the downstream end issues fresh pull requests
as its own buffer drains. Each pull drains the upstream buffer and
unblocks the upstream driver.

## The feedback loop

1. Upstream produces a page → output buffer fills.
2. Buffer hits its cap → upstream driver goes BLOCKED.
3. Downstream consumes a page → exchange client pulls more.
4. Pull drains the upstream buffer → upstream driver unblocks.
5. Upstream runs again → produces another page.

The loop self-regulates to the slowest stage's rate. Each stage's pull
demand naturally throttles its upstream.

## Why it matters

Backpressure keeps memory bounded without any central data-flow
controller. The same loop also protects the source system — a slow
downstream means the connector reads slower from S3 or PostgreSQL,
rather than draining the external system as fast as it can deliver.

---

Return to [Trino](_index.md)
