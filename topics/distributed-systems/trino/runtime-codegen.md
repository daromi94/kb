# Runtime code generation

Trino is written in Java, but its hot-path operators do not run as
handwritten Java. For each query, Trino generates JVM bytecode tailored to
that query's specific operators, expressions, and types, then loads it into
the running JVM.

## Why generate code

A generic interpreter — one that walks an expression tree at runtime to
evaluate `a + b * 2 > c` for every row — pays for indirection on every
operation: virtual calls, type dispatch, boxing of primitives. That overhead
is acceptable per row in a transactional database; it is fatal when scanning
billions of rows.

Generated code collapses the tree into straight-line, monomorphic JVM
bytecode that:

- Eliminates virtual dispatch on operators and expressions.
- Inlines arithmetic on primitive types directly.
- Lets the JVM's JIT optimize it further: SIMD vectorization, loop
  unrolling, escape analysis.

The end result is a per-query tight inner loop competitive with a
handwritten native engine.

## What gets generated

| Component           | What is specialized                             |
|---------------------|-------------------------------------------------|
| Expression compiler | Per-expression bytecode for filters/projections |
| Operator factories  | Hash join, aggregation, scan loops              |
| Page processors     | Column-by-column iteration over pages           |

Generation is on-demand and cached: the first execution of a query pays the
codegen cost; subsequent executions of the same shape reuse the compiled
class.

## Trade-off

Codegen adds latency to the first execution and consumes JVM metaspace for
generated classes. In return, the per-row cost on the hot path drops by an
order of magnitude or more. For analytical queries scanning millions of
rows, this is a clear win.

---

Return to [Trino](_index.md)
