# Shard-per-Core Architecture

ScyllaDB's shard-per-core architecture tightly couples database software to
hardware. Instead of treating a server as one large pool of resources, ScyllaDB
splits it into independent processing units—one per physical CPU core. Each
unit is called a **shard**.

This architecture is built on the **Seastar** C++ framework.

## Shared-Nothing Design

In most databases, threads share memory and compete for locks. In ScyllaDB,
each core is a fully independent worker that shares nothing with other cores.

**One shard = one core.** A server with 32 CPU cores creates 32 independent
shards.

**Total ownership.** Each shard completely owns:
- A specific slice of the dataset (based on the token ring)
- A dedicated chunk of RAM
- A dedicated slice of network bandwidth

**No locks.** Because a shard is the only thing that can access its data and
memory, it needs no locking mechanisms. This eliminates CPU overhead wasted on
waiting for locks.

## Mechanical Details

**Thread-per-core.** ScyllaDB pins one system thread to each physical CPU core.
This thread runs a userspace task scheduler that manages all operations—reads,
writes, compaction, replication—for that core.

**Message passing.** If Core 1 needs data on Core 2, it sends an asynchronous
message rather than reaching into Core 2's memory. This resembles how servers
communicate over a network, but happens inside the CPU at high speed.

**NUMA awareness.** Modern servers have Non-Uniform Memory Access where
accessing RAM on a different CPU socket is slower. ScyllaDB ensures a shard on
Socket A primarily uses RAM attached to Socket A, preventing expensive
cross-socket memory trips.

## Thread-Pool vs Shard-per-Core

| Feature     | Thread-Pool (Cassandra)            | Shard-per-Core (ScyllaDB)         |
| ----------- | ---------------------------------- | --------------------------------- |
| Concurrency | Hundreds of threads compete for    | One thread per core. No context   |
|             | CPU. OS constantly context switches| switching; CPU does actual work   |
| Memory      | Shared heap. Threads contend for   | Partitioned. Core 0 owns its      |
|             | access, requiring locks            | chunk. No contention              |
| I/O         | Blocking. Threads sleep waiting    | Async (Seastar). Core switches to |
|             | for disk/network                   | another task without sleeping     |

## Benefits

**Linear scalability.** Doubling cores yields nearly double throughput. Thread
pools see diminishing returns from lock contention.

**Predictable latency.** Removing thread contention and garbage collection
pauses keeps P99 latencies low and stable.

**Better hardware utilization.** The same workload runs on fewer servers
because CPUs aren't wasting cycles managing threads or waiting for locks.

## Analogy

Traditional (Cassandra): 50 chefs share one giant cutting board. They
constantly bump into each other waiting for the knife.

ScyllaDB: 32 separate stations. Each has one chef, one cutting board, one set
of ingredients. They never collide and work at maximum speed.
