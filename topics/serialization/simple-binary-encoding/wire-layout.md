# Wire layout

Every SBE message follows a strict, forward-only layout. Fixed fields
are always at deterministic offsets from the start of their block, which
is what gives SBE its speed.

## Message structure

```
+---------------------------------------------+
| Message header                              |
|   blockLength | templateId | schemaId | ver |
+---------------------------------------------+
| Root block (fixed-size fields)              |
|   Fields at known offsets within the block  |
+---------------------------------------------+
| Repeating groups                            |
|   Each: dimension header + entries          |
+---------------------------------------------+
| Variable-length data (varData)              |
|   Length-prefixed strings and byte blobs    |
+---------------------------------------------+
```

The ordering is enforced: fixed fields before groups, groups before
varData. This constraint applies recursively within groups.

## Message header

The header identifies the message type and enables forward
compatibility. The reference implementation uses an 8-byte header with
four uint16 fields:

| Field       | Purpose                         |
|-------------|---------------------------------|
| blockLength | Size of the root block in bytes |
| templateId  | Identifies the message type     |
| schemaId    | Identifies the schema           |
| version     | Schema version for evolution    |

## Root block

All fixed-size fields (integers, enums, bitsets) are laid out
sequentially at deterministic offsets. The codec knows every field's
position at compile time — a field read is just
`buffer.getInt(offset + N)`.

## Repeating groups

Ordered collections follow the root block. Each group starts with a
dimension header (blockLength + numInGroup) followed by entries. Groups
can contain nested fixed fields, nested groups, and trailing varData.
Groups must be iterated sequentially — random access within a group is
not supported because preceding variable-length entries shift offsets.

## Variable-length data

Strings and arbitrary byte arrays go last so they cannot shift the
offsets of fixed fields. Each varData field is length-prefixed.

## Related

- [Overview](overview.md) - Why this layout exists
- [Schema evolution](schema-evolution.md) - blockLength-based skipping

---

Return to [Simple Binary Encoding](_index.md)
