# Naming

Names deserve significant investment. Good names capture precise meaning
and prevent misunderstanding.

## General principles

- Find nouns and verbs that convey exact meaning
- No abbreviations except primitive loop variables
- Avoid overloading names across different contexts
- Prefer nouns over adjectives for composability

## Casing

- `snake_case` for functions, variables, and files
- Capitalize acronyms properly: `VSRState` not `VsrState`

## Units and qualifiers

Append units or qualifiers to names, ordered by descending significance:

- `timeout_ms` not `timeout`
- `buffer_bytes` not `buffer_size`

Pick related names with equal character counts for visual alignment when
practical.

## Functions

- Prefix helpers with the calling function's name to show call hierarchy
- Place callbacks last in parameter lists, mirroring invocation order

## File organization

- Order contents top-to-bottom by importance; `main` goes first
- Nested types: fields, then type definitions, then methods

## Arguments

- Use named arguments when parameters could be confused
- Provide explicit option values at call sites rather than relying on
  defaults

## Comments and commits

- Comments explain rationale, not what the code does
- Format comments as proper sentences
- Write commit messages for the reader, not the author

## Related

- [Overview](overview.md) - Developer experience as a core priority
- [Safety](safety.md) - How naming clarity prevents bugs

---

Return to [TigerStyle](_index.md)
