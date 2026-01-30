# ScyllaDB

A high-performance NoSQL database compatible with Apache Cassandra, built in
C++ on the Seastar framework. Known for its shard-per-core architecture that
eliminates thread contention.

## Notes

- [Shard-per-core](shard-per-core.md) - Thread-per-core architecture for linear scalability
- [Bloom filters](bloom-filters.md) - Probabilistic data structure for fast set membership
- [Commit log](commit-log.md) - Append-only durability mechanism for crash recovery
