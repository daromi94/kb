# Specialized data subsystems

A data-intensive application is assembled from specialized subsystems, each
optimized for one data structure and access pattern, rather than built on a
single database that serves every need. Forcing one database to handle
conflicting access patterns — point writes, full-text search, analytics
scans — causes resource contention and latency spikes. Splitting the
workload across purpose-built stores lets each handle the access pattern it
was engineered for.

## Building blocks

| Subsystem        | Purpose                   | How it works                                 |
|------------------|---------------------------|----------------------------------------------|
| Database         | Durable system of record  | Persists state to disk via a write-ahead log |
| Cache            | Faster reads              | Serves results from memory, bypassing disk   |
| Search index     | Search and filtering      | Inverted index maps terms to documents       |
| Stream processor | Low-latency reactions     | Processes append-only logs as events arrive  |
| Batch processor  | High-throughput analytics | Parallel passes over bounded historical data |
