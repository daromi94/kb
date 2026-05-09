# Schema evolution

SBE schema evolution is additive-only. This is more restrictive than
Protobuf but guarantees the deterministic layout that SBE depends on.

## Rules

- Append new fields at the end of a block, tagged with `sinceVersion`
- Never remove, reorder, or change the type of existing fields
- New repeating groups go after existing groups
- New varData fields go after existing varData fields
- Incompatible changes require a new templateId

## How it works

Older decoders skip unknown trailing fields using the blockLength value
from the message header (or group dimension header). The blockLength
tells the decoder how many bytes to read for the block it understands —
anything beyond that is silently skipped.

The `sinceVersion` attribute on new fields is schema metadata for
documentation and validation. It is not encoded on the wire. The
version field in the message header tells the decoder which schema
version produced the message, so it can apply default values for fields
added after its own schema version.

## Constraints vs Protobuf

| Capability         | SBE | Protobuf |
|--------------------|-----|----------|
| Add fields         | Yes | Yes      |
| Remove fields      | No  | Yes      |
| Reorder fields     | No  | Yes      |
| Optional fields    | No  | Yes      |
| Change field types | No  | Limited  |

The tradeoff is flexibility for performance — SBE locks down the layout
so every field access remains a direct offset read.

---

Return to [Simple Binary Encoding](_index.md)
