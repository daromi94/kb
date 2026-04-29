# Replication

Replication is Ceph's fundamental mechanism for data durability and high
availability. Multiple identical copies of every object are maintained across
different physical nodes.

## Primary-copy model

Ceph uses synchronous, primary-copy replication. For any piece of data, one OSD
is the "Primary" responsible for coordinating writes to all "Secondary"
replicas.

1. **Client submission:** Client sends data to Primary OSD (determined by CRUSH)
2. **Parallel replication:** Primary writes locally and forwards to Secondaries
3. **Replica acknowledgment:** Secondaries write and ACK back to Primary
4. **Commit:** Primary confirms to client after its own write + all replica ACKs

## Key parameters

Two pool parameters control replication:

**`size`:** Total copies to maintain (default: 3)

**`min_size`:** Minimum replicas required to ACK before success (default: 2)

If active OSDs for a PG fall below `min_size`, Ceph stops accepting I/O for
that PG to prevent inconsistency.

## Replication vs erasure coding

| Feature            | Replication          | Erasure Coding (EC)           |
|--------------------|----------------------|-------------------------------|
| Storage Efficiency | Low (33% for size 3) | High (66%+ for typical k+m)   |
| CPU/RAM Usage      | Low                  | High (encode/decode overhead) |
| Recovery Speed     | Fast (simple copy)   | Slower (math reconstruction)  |
| Best For           | Small, random I/O    | Large, sequential I/O         |

## Fault domains

Replication is only effective if copies are physically separated. CRUSH ensures
replicas land on different disks, servers, or racks based on configuration.

| Failure Domain | Protection Level       |
|----------------|------------------------|
| `osd`          | Single disk failure    |
| `host`         | Entire server failure  |
| `rack`         | Entire rack power loss |
| `datacenter`   | Site-level disaster    |

## Self-Healing (backfilling)

When an OSD fails:

1. **Degraded state:** PGs with data on that OSD are degraded but accessible
   (if `min_size` is met)
2. **Detection:** Surviving OSDs and Monitors detect the failure
3. **Backfilling:** Cluster identifies new homes for missing replicas and copies
   data to restore full `size` count

## Related

- [Read and write paths](read-write-paths.md) - How replication fits in I/O flow
- [CRUSH algorithm](crush-algorithm.md) - How replica locations are determined
- [Consistency model](consistency.md) - Why synchronous replication matters

---

Return to [Ceph](_index.md)
