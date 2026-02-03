# TigerStyle safety

TigerStyle's safety principles derive from NASA's Power of Ten guidelines,
fundamentally reshaping coding practices to prevent defects before they occur.

> "The rules act like the seat-belt in your car: initially they are perhaps a
> little uncomfortable, but after a while their use becomes second-nature and
> not using them becomes unimaginable." — Gerard J. Holzmann

## Control flow and structure

- Restrict yourself to straightforward, transparent control mechanisms
- Eliminate recursion to guarantee bounded execution
- Apply only minimal, genuinely valuable abstractions; every abstraction carries
  inherent risk
- Establish upper bounds on all operations (loops, queues, memory) following
  fail-fast principles

## Type safety

Use explicitly-sized types (`u32`) exclusively. Avoid architecture-dependent
types like `usize` that introduce platform-specific behavior.

## Memory management

- Allocate all memory statically at startup
- Prohibit dynamic allocation after initialization
- This restriction paradoxically produces simpler, more efficient, and more
  maintainable designs

## Scope and complexity

- Declare variables at minimal scope; minimize active variables
- Enforce a strict 70-line maximum per function. Physical constraints drive
  creative solutions
- Group control flow in parent functions; move computation to pure helper
  functions ("push ifs up and fors down")
- Centralize state manipulation within parent functions; helpers compute changes
  rather than applying them

## External interactions

- React to external events indirectly rather than in direct response
- Maintain independent program pace through batching rather than event-driven
  context switching
- Preserve program control flow and enable performance optimization
  simultaneously

## Error handling

Analysis reveals that approximately 92% of catastrophic failures result from
inadequate handling of explicitly signaled non-fatal errors. Comprehensive error
handling remains non-negotiable.

## Related

- [Assertions](assertions.md) - Detailed assertion strategy
- [Performance](performance.md) - How batching enables safety without cost
- [Overview](overview.md) - Safety as the top priority
