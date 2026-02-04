# Read and Write Paths

Ceph's read and write paths are governed by the **Primary OSD model**. One OSD
coordinates all I/O for any given Placement Group, ensuring strict data
consistency.

## Write Path

Ceph prioritizes strong consistency. A write succeeds only after all replicas
acknowledge.

1. **Client calculation:** Using `librados` or a high-level driver, the client
   runs CRUSH to find which OSD is Primary for the target PG.

2. **Request submission:** Client sends write directly to Primary OSD.

3. **Primary write:** Primary writes to its local BlueStore backend.

4. **Replication:** Simultaneously, Primary forwards the request to all
   Secondary OSDs in the acting set.

5. **Replica acknowledgment:** Each Secondary writes locally and ACKs the
   Primary.

6. **Client acknowledgment:** Once Primary confirms its own write and receives
   all replica ACKs, it notifies the client of success.

```
Client
   |
   | write
   v
Primary OSD -----> Secondary OSD 1
   |                    |
   |                    | ACK
   |<-------------------+
   |
   +-------------> Secondary OSD 2
   |                    |
   |                    | ACK
   |<-------------------+
   |
   | ACK
   v
Client
```

**BlueStore detail:** The write is "committed" once safely in the Write-Ahead
Log (WAL), even before flushing to the main data disk.

## Read Path

Reads are simpler---usually a single network hop.

1. **Client calculation:** CRUSH identifies the Primary OSD.
2. **Direct read:** Client requests data from Primary.
3. **Local retrieval:** Primary reads from BlueStore, performs checksum.
4. **Return:** Data sent directly to client.

## Erasure Coded Pools

In EC pools, the write path is more complex:

- Primary receives data
- Breaks it into $k$ data chunks and $m$ coding chunks
- Distributes $k+m$ chunks across different OSDs

Reads require fetching at least $k$ chunks to reconstruct the original object.

## Read from Replica

While Ceph typically reads from Primary for consistency, certain configurations
allow **localized reads**. If a client is geographically closer to a replica,
it can read from that replica to reduce latency (requires specific pool
settings).

## Comparison

| Aspect         | Write Path                         | Read Path                |
|----------------|------------------------------------|--------------------------|
| Primary Actor  | Primary OSD                        | Primary OSD (typically)  |
| Consistency    | Strong (all replicas must ACK)     | High (read from Primary) |
| Network Hops   | Client → Primary → Replicas        | Client → Primary         |
| Load           | High (hashing, WAL, replication)   | Low (hashing, local read)|

## Related

- [Replication](replication.md) - How replicas are managed
- [Consistency](consistency.md) - The CAP trade-offs

---

Return to [Ceph](_index.md)
