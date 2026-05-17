# Safety

Safety principles derived from NASA's Power of Ten guidelines.

## Control flow

- Use straightforward control mechanisms only
- No recursion — guarantees bounded execution
- Minimize abstractions; every abstraction carries risk
- Set upper bounds on all loops, queues, and memory allocations

## Type safety

Use explicitly-sized types (`u32`) only. Avoid architecture-dependent types
like `usize` that introduce platform-specific behavior.

## Memory management

Allocate all memory statically at startup. No dynamic allocation after
initialization.

## Scope and complexity

- Declare variables at minimal scope
- Strict 70-line maximum per function
- Push control flow up into parent functions, push computation down into
  pure helpers ("push ifs up and fors down")
- Parent functions own state changes; helpers compute but don't apply them

## External interactions

React to external events through batching rather than direct event-driven
dispatch. This preserves predictable control flow and enables performance
optimization.

## Error handling

~92% of catastrophic failures stem from mishandled non-fatal errors that
were explicitly signaled. Handle every error.

---

Return to [TigerStyle](_index.md)
