# PIE heuristic

PIE is a heuristic for database selection: a database can be optimized
for at most two of three properties — pattern flexibility, infinite
scale, and efficiency.

- **Pattern flexibility (P):** Support ad-hoc queries as access
  patterns evolve.
- **Infinite scale (I):** Partition horizontally without performance
  degradation.
- **Efficiency (E):** Serve high concurrency at millisecond latency.

## The three corners

| Corner | Sacrifices          | Typical category                |
|--------|---------------------|---------------------------------|
| PE     | Infinite scale      | Relational, normalized          |
| IE     | Pattern flexibility | Distributed NoSQL, denormalized |
| PI     | Efficiency          | Columnar, batch analytics       |

**PE.** Normalized models keep queries flexible. Scaling is vertical;
distributed joins are slow. Examples: PostgreSQL, MySQL.

**IE.** Data is pre-assembled for known access patterns, so reads are
single-node lookups. New access patterns require migrations.
Examples: DynamoDB, Cassandra.

**PI.** Columnar engines scan and aggregate massive datasets at
second-to-hour latency. Not suited for transactional traffic.
Examples: Snowflake, Redshift.

## Why "pick two" holds

The mechanism is data locality:

1. Horizontal scale forces a **partition key**.
2. A partition key forces data to be **co-located** with its queries.
3. Co-location means access patterns are **decided up front** —
   exactly what pattern flexibility gives up.

You cannot simultaneously have a normalized model, horizontal
partitioning, and arbitrary low-latency cross-entity joins.

## Where the corners blur

Distributed SQL (Spanner, CockroachDB, TiDB, Yugabyte) targets the
"P and I with reasonable E" corner via consensus replication and range
partitioning. Cross-shard transactions still pay coordination latency,
so "pick two" reads as **the third costs you measurably**, not that
it's unreachable.

---

Return to [Databases](_index.md)
