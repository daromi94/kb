# Zero dependencies

TigerBeetle allows zero dependencies beyond the Zig toolchain. This applies
to both runtime libraries and development tools.

## Why

Dependencies introduce compounding risks for foundational infrastructure:

- **Supply chain risk:** External code may be compromised or abandoned
- **Safety hazards:** Unvetted code violates safety principles
- **Performance costs:** General-purpose libraries optimize for flexibility,
  not speed
- **Deployment friction:** Each dependency multiplies installation complexity

## Tooling

One toolchain for everything. Zig covers builds, formatting, and
analysis — no need for language-specific tools that fragment team velocity.

> "The right tool for the job is often the tool you are already using—adding
> new tools has a higher cost than many people appreciate" — John Carmack

## Trade-offs

Higher upfront implementation cost, lower long-term maintenance burden. For
infrastructure intended to run for decades, self-contained code provides
stronger guarantees than external dependencies.

---

Return to [TigerStyle](_index.md)
