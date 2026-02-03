# TigerStyle assertions

Assertions identify programmer errors. They represent the correct response to
corrupt code, catching bugs at the earliest possible moment.

## Assertion strategy

- Validate all function arguments, return values, preconditions, postconditions,
  and invariants
- Target a minimum average of two assertions per function
- Employ dual assertions for critical properties: check validity before writing
  data and again after reading
- Prefer simple, single-line assertions over compound conditions
- Split compound assertions: `assert(a); assert(b);` over `assert(a and b);`

## Implication checks

Use `if (a) assert(b);` syntax for implication checks. This expresses "if
condition A holds, then condition B must also hold" without failing when A is
false.

## Compile-time validation

Validate compile-time constant relationships as design sanity checks. These
assertions cost nothing at runtime and catch configuration errors during
compilation.

## Boundary testing

Assert both valid and invalid conditions. Intersection points between valid and
invalid boundaries reveal subtle bugs that single-sided checks miss.

## Limitations

Assertions complement rather than replace human understanding. They catch bugs
but do not prove correctness. Design thinking remains essential.

## Related

- [Safety](safety.md) - Broader safety principles
- [Overview](overview.md) - Why rigorous validation matters

---

Return to [TigerStyle](_index.md)
