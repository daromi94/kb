# HBase data model

HBase stores data in a sparse, multidimensional map indexed by row key, column
family, column qualifier, and timestamp.

## Structure

```
Row Key -> Column Family -> Column Qualifier -> Timestamp -> Value

Example:
"user123" -> "info" -> "name"  -> 1699000000 -> "Alice"
                    -> "email" -> 1699000000 -> "alice@example.com"
          -> "logs" -> "login" -> 1699000001 -> "2024-01-15"
```

## Components

**Row key:** The unique identifier for a row. Data is **lexicographically
sorted** by row key (as a byte array). This sorting is critical for range scan
performance—adjacent keys are stored together on disk.

**Column family:** A group of columns physically stored together. Column
families must be defined upfront when creating the table. Examples: `info`,
`logs`, `metrics`.

**Column qualifier:** The specific attribute within a family. Qualifiers can be
created on the fly without schema changes. Examples: `info:name`, `info:email`.

**Timestamp:** Every cell is versioned by timestamp, enabling queries for
historical data. Multiple versions of the same cell can coexist.

## Sparse storage

The data model is sparse—nulls take up no storage space. Unlike relational
databases where every row has the same columns, HBase rows can have completely
different column qualifiers within the same column family.

```
Row "user1": info:name, info:email
Row "user2": info:name, info:phone, info:address
Row "user3": info:email
```

Each row only stores the columns it actually has values for.

## Design considerations

- **Row key design is critical:** Since data is sorted by row key, the key
  structure determines access patterns. Avoid monotonically increasing keys
  (like timestamps) which create hotspots.
- **Column families are heavyweight:** They affect physical storage layout.
  Use a small number (typically 1-3) of well-chosen families.
- **Column qualifiers are lightweight:** Add freely as needed without schema
  changes.

## Related

- [Storage engine](storage-engine.md) - How this model maps to physical storage
