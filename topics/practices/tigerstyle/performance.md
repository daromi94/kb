# TigerStyle performance

TigerStyle treats performance as a design-phase concern rather than an
afterthought. Preliminary sketches targeting resource constraints prevent
architectural mistakes that no amount of later optimization can fix.

> "The lack of back-of-the-envelope performance sketches is the root of all
> evil." — Rivacindela Hudsoni

## Design-phase optimization

- Consider performance implications from project inception
- Conduct preliminary performance sketches targeting the four resources:
  network, disk, memory, CPU
- Achieve "roughly correct" estimates reaching approximately 90% of theoretical
  maximum
- Address slowest resources first, adjusted for usage frequency

## Batching

Batching is the central optimization technique, amortizing costs across all four
resource types:

- Distinguish control and data planes; leverage batching for assertion safety
  without performance costs
- Amortize network, disk, memory, and CPU expenses through batching
- Provide CPUs large work units rather than forcing frequent context switching

## Hot loops

Extract hot loops into standalone functions with primitive arguments. This
facilitates compiler optimization by:

- Reducing function complexity visible to the optimizer
- Enabling better inlining decisions
- Allowing the compiler to focus optimization effort on critical paths

## Related

- [Safety](safety.md) - How batching enables safety without performance cost
- [Overview](overview.md) - Performance as the second priority after safety

Return to [TigerStyle](_index.md)
