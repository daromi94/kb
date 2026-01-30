# Schema Evolution

In distributed systems, updating a data structure often breaks services that
haven't been updated yet. Protobuf solves this through backward and forward
compatibility.

## The Problem

Changing data structures can invalidate existing data or require a synchronized
"big bang" update across all servers.

## Compatibility Mechanisms

**Backward compatibility:** Newer binaries can handle the absence of old fields
without crashing. Missing fields receive default values.

**Forward compatibility:** Older binaries can ignore new fields they don't
recognize. The skip logic in the wire format makes this possible.

## Why It Works

Fields are identified by numeric tags rather than names. This makes the
structure extensible without changing the underlying parsing logic.

Adding a new field with a new tag number doesn't affect existing code—it simply
skips the unknown tag. Removing a field doesn't break newer code—it uses the
default value when the tag is absent.

## Rules for Safe Evolution

- Never reuse a field number for a different field
- Never change the type of an existing field
- New fields should use new tag numbers
- Mark removed fields as `reserved` to prevent accidental reuse

## Summary

| Problem          | Protobuf Solution                            |
|------------------|----------------------------------------------|
| Breaking changes | Field numbers allow seamless schema updates  |
| Type mismatches  | Strictly typed definitions in `.proto` files |
| Missing fields   | Default values for absent tags               |
| Unknown fields   | Skip logic ignores unrecognized tags         |

## Related

- [Wire format](wire-format.md) - How skip logic enables compatibility
- [Architecture](architecture.md) - The role of the `.proto` schema
