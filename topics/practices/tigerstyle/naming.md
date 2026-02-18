# Naming

Exceptional names capture essence and facilitate intuitive understanding. Naming
is one of the hardest problems in computer science, deserving significant
investment.

## General principles

- Invest effort in discovering nouns and verbs conveying precise meaning
- Avoid abbreviations except for primitive loop variables
- Avoid context-dependent name overloading
- Choose nouns over adjectives for composability in documentation

## Casing conventions

- Apply `snake_case` for functions, variables, and files
- Capitalize acronyms properly: `VSRState` not `VsrState`

## Units and qualifiers

Append units or qualifiers to variable names, positioned by descending
significance. This prevents confusion between related quantities:

- `timeout_ms` rather than `timeout`
- `buffer_bytes` rather than `buffer_size`

Select related names with equivalent character counts for visual alignment when
practical.

## Function naming

- Prefix helper functions with calling function names to indicate call hierarchy
- Place callbacks last in parameter lists, mirroring invocation order

## File organization

- Order file contents top-to-bottom by importance; position `main` first
- Structure nested types: fields, then type definitions, then methods

## Arguments and parameters

- Employ named arguments when parameters might be confused
- Provide explicit option values at call sites rather than relying on defaults

## Comments and commits

- Write substantive comments explaining rationale and methodology
- Format comments as proper sentences with appropriate punctuation
- Compose descriptive commit messages addressing reader interest

## Related

- [Overview](overview.md) - Developer experience as a core priority
- [Safety](safety.md) - How naming clarity prevents bugs

---

Return to [TigerStyle](_index.md)
