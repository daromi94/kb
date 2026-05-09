# Assertions

Assertions catch programmer errors by validating assumptions at runtime.
They are the correct response to corrupt internal state.

## Strategy

- Validate all function arguments, return values, preconditions,
  postconditions, and invariants
- Target at least two assertions per function on average
- Use dual assertions for critical properties: check before writing, check
  again after reading
- Keep assertions simple and single-line
- Split compound conditions: `assert(a); assert(b);` not `assert(a and b);`

## Implication checks

Use `if (a) assert(b);` for implication checks — "if A holds, then B must
also hold." Does not fire when A is false.

## Compile-time validation

Validate constant relationships at compile time. These cost nothing at
runtime and catch configuration errors during builds.

## Boundary testing

Assert both valid and invalid conditions. The intersection between valid
and invalid boundaries reveals bugs that single-sided checks miss.

## Limitations

Assertions catch bugs but do not prove correctness. Design thinking remains
essential.

---

Return to [TigerStyle](_index.md)
