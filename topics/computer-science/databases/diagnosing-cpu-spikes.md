# Diagnosing CPU spikes

When a database pegs at 100% CPU, the cause is almost always the workload —
not configuration, not hardware.

## Start with active sessions

Look at the engine's list of running queries. Three patterns point at
different causes:

- A few long-running queries dominating the CPU
- Many sessions in a runnable state — CPU-ready, not waiting
- A flood of fast queries, thousands per second of the same shape

## Missing indexes

The most common cause. Without an index, a query selecting 5 rows from a
50M-row table pulls all 50M rows through the CPU for comparison. If the
table is cached, the disk graph stays calm while the CPU pegs.

**Action:** Pull the execution plans of the top CPU consumers. Replace
sequential scans with index seeks where selectivity justifies it.

## Bad cached plans

A plan compiled for one parameter set can be catastrophic for another. A
query that normally returns 1 row gets a Nested Loop join; later called
for 10M rows, it reuses the cached plan and burns orders of magnitude more
CPU than the Hash Join it should have picked.

**Action:** Watch for the same query hash with wildly variable runtime.
Flush the offending plan to force re-compilation.

## Ad-hoc query compilation

If the application sends literal SQL — `WHERE id = 123` instead of
`WHERE id = ?` — the engine cannot reuse plans. Every execution pays the
full optimizer cost, turning the database into a compilation engine.

**Action:** Track the ratio of compilations to queries — a high ratio
means the engine is compiling more than running. Convert ad-hoc
statements to parameterized or prepared queries.

## Connection storms

A reconnect flood burns CPU on authentication and session setup — TLS
handshakes, login validation, worker thread allocation, per-session
memory. Under sustained high concurrency, threads also contend for shared
in-memory structures and burn cycles spinning on latches rather than
running queries.

**Action:** Place a connection pool in front of the database to cap
concurrency and keep authenticated connections warm.

## Decision summary

| Symptom                               | Likely cause                 |
|---------------------------------------|------------------------------|
| Single query dominates CPU            | Missing index or bad plan    |
| Same query, variable runtime          | Parameter-sensitive plan     |
| Thousands of distinct query texts/sec | Ad-hoc compilation           |
| CPU spike correlates with reconnects  | Connection storm, no pooling |
| High CPU, low query throughput        | Latch contention             |

---

Return to [Databases](_index.md)
