# Data model

DynamoDB organizes data into tables, items, and attributes. Its key
structure determines both how items are identified and where they are
physically stored.

## Table structure

A table is a collection of items. Each item is a collection of
attributes. Items are analogous to rows and attributes to columns,
but the schema is flexible — only the primary key attributes are
required on every item. All other attributes can vary between items.

## Primary keys

The primary key schema is defined at table creation and cannot be
changed. There are two types:

| Type      | Components               | Uniqueness constraint                             |
|-----------|--------------------------|---------------------------------------------------|
| Simple    | Partition key only       | Each partition key value must be unique           |
| Composite | Partition key + sort key | Partition key can repeat; the pair must be unique |

## Partition placement

The partition key determines physical data placement:

1. The partition key value is passed through an internal hash
   function.
2. The hash output maps the item to a specific storage partition.
3. If a sort key exists, items sharing the same partition key are
   stored in sorted order by sort key within that partition.

This hashing scheme lets the request router contact the correct
storage node directly without scanning, maintaining single-digit
millisecond latency regardless of table size.

## Related

- [Partitioning and replication](partitioning-and-replication.md) - Partition placement
- [Performance](performance.md) - Routing and admission control

---

Return to [DynamoDB](_index.md)
