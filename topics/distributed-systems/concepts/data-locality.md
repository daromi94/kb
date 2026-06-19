# Data locality

Computation runs fastest when the data it needs sits physically close.
Each step outward through the memory, storage, and network hierarchy
costs more.

## Locality of reference

Within a single machine, locality of reference is the tendency of a
program to reuse data that is close in time or in address space. Temporal
locality means data used recently is likely to be used again soon.
Spatial locality means data next to a recent access is likely to be
needed next.

Caches, prefetchers, and the register → cache → main memory → disk
hierarchy all exist to exploit both. A cache hit can be orders of
magnitude faster than a trip to main memory.

Even main memory has a near and a far. Under NUMA (non-uniform memory
access), a core reaches the bank attached to its own socket faster than
one attached to another socket on the same board.

## Across a cluster

The same principle scales up. A node's own memory and local disk are
close, while another machine across the network is far. Reading a block
from a local disk costs far less than pulling it over the network. A task
placed on the machine that already holds its input avoids that cost
entirely.

Network bandwidth in a large cluster is much lower than the aggregate
bandwidth of all its disks. Keeping reads local both speeds up the task
and spares the network backplane — a shared, finite resource — for work
that needs it.

## The locality hierarchy

A scheduler ranks placements on a physical spectrum and tries to satisfy
each task at the closest available tier:

| Tier          | Where the data sits             | Network cost             |
|---------------|---------------------------------|--------------------------|
| Node-local    | same machine, local disk/memory | zero transfer            |
| Rack-local    | another node in the same rack   | one top-of-rack switch   |
| Cluster-local | another rack, same datacenter   | traverses the core spine |
| Cross-region  | separate datacenter or region   | wide-area latency        |

The scheduler prefers node-local placement and degrades to the next tier
when the ideal node is busy, rather than leaving the task queued. Replica
placement makes the near tiers likely. A common pattern keeps one replica
on the local node, one elsewhere in the same rack, and one on a separate
rack — fault tolerance balanced against the chance of a node-local read.

## Trade-offs

Locality couples compute to storage. The machines that hold the data
must also run the code, so the two cannot scale independently. A node can
exhaust its CPU while its disk sits half-empty.

Concentrating work where the data lives also concentrates load. A hot
partition saturates the single node that holds it while nodes holding
cold data idle.

Locality serves a bottleneck; it is not a goal in itself. Profile where
the time goes — network, CPU, or disk — before restructuring for it. A
CPU-bound job, or one on a network fast enough that remote reads are
cheap, gains nothing from chasing locality and loses flexibility.

---

Return to [Concepts](_index.md)
