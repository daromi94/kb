# Performance

Performance is a design-phase concern. Back-of-the-envelope sketches
targeting resource constraints prevent architectural mistakes that no later
optimization can fix.

## Design-phase sketches

- Estimate against the four resources: network, disk, memory, CPU
- Aim for ~90% of theoretical maximum ("roughly correct")
- Address the slowest resource first, adjusted for access frequency

## Batching

The central optimization technique. Batching amortizes costs across all
four resource types:

- Separate control plane from data plane; batch the data plane
- Give CPUs large work units instead of frequent small ones
- Batching also enables assertion-heavy code without performance cost —
  checks run on the control plane, not inside the hot path

## Hot loops

Extract hot loops into standalone functions with primitive arguments. This
helps the compiler by reducing function complexity, enabling better
inlining, and focusing optimization on the critical path.

---

Return to [TigerStyle](_index.md)
