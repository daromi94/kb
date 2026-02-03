# HBase

Distributed, column-oriented NoSQL database built on HDFS, modeled after
Google's Bigtable.

## Notes

- [Overview](overview.md) - High-level concept and use cases
- [Architecture](architecture.md) - Master/Slave model with HMaster and RegionServers
- [Data model](data-model.md) - Row keys, column families, qualifiers, timestamps
- [Storage engine](storage-engine.md) - LSM tree with WAL, MemStore, and HFiles
- [Consistency model](consistency-model.md) - CP system with single-owner guarantees
- [Netty I/O](netty-io.md) - Event-driven RPC and async WAL
