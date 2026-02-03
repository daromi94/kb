# TigerStyle zero dependencies

TigerBeetle maintains a zero dependencies policy beyond the Zig toolchain. This
applies to both runtime libraries and development tools.

## Why avoid dependencies

Dependencies introduce compounding risks for foundational infrastructure:

- **Supply chain risk:** External code may be compromised or abandoned
- **Safety hazards:** Unvetted code violates safety principles
- **Performance costs:** General-purpose libraries optimize for flexibility, not
  speed
- **Installation complexity:** Each dependency multiplies deployment friction

## Tooling standardization

Specialized tools fragment team velocity. The Zig toolchain provides sufficient
capability across domains, eliminating the need for language-specific build
systems, formatters, or analyzers.

> "The right tool for the job is often the tool you are already using—adding new
> tools has a higher cost than many people appreciate" — John Carmack

## Trade-offs

This policy increases upfront implementation cost but reduces long-term
maintenance burden. For foundational infrastructure intended to run for decades,
self-contained code provides stronger guarantees than external dependencies.

## Related

- [Overview](overview.md) - Philosophy of sustainable design
- [Safety](safety.md) - How dependencies violate safety principles

---

Return to [TigerStyle](_index.md)
