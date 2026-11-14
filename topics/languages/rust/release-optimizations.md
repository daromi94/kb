# Release optimizations

**Release optimizations are compiler transformations that improve the performance, memory efficiency, and sometimes binary size of a Rust program before it executes.**

Rust has two primary build profiles:

```bash
cargo build             # Development profile
cargo build --release   # Release profile
```

Both produce native machine code, but they instruct the compiler to prioritize different goals.

- **Development builds:** Fast compilation and effective debugging.
- **Release builds:** Faster execution and optimized machine code, usually at the cost of longer compilation times.

## 1. How release compilation works

Rust performs its most important runtime optimizations through its compiler backend, typically LLVM.

```text
              Rust Source
                   |
                   v
             Rust Frontend
                   |
                   v
             Type checking
                   |
                   v
            Borrow checking
                   |
                   v
                  MIR
                   |
                   v
                LLVM IR
                   |
      +------------+------------+
      |                         |
      v                         v
    DEBUG                    RELEASE
      |                         |
      v                         v
   Minimal                 Aggressive
optimization              optimization
      |                         |
      v                         v
   Machine                   Machine
    Code                      Code
      |                         |
      v                         v
Debug Binary             Release Binary
```

The significant difference is what happens during code optimization.

**The release compiler can transform the original program substantially, provided it preserves the required observable behavior.**

This last constraint is fundamental: **optimization is not about executing the source instructions more quickly. It is about generating different instructions that produce equivalent results.**

## 2. Common release optimizations

### Constant folding

Consider:

```rust
fn calculate() -> i32 {
    let a = 10;
    let b = 20;

    (a + b) * 2
}
```

The compiler can determine that the result is always `60`.

Conceptually:

```text
Original:
    a = 10
    b = 20
    c = a + b
    result = c * 2

Optimized:
    result = 60
```

There is no need to perform those arithmetic operations at runtime.

### Dead code elimination

**Code whose result cannot affect observable program behavior can be removed.**

```rust
fn calculate(x: i32) -> i32 {
    let unused = x.wrapping_mul(100);
    x + 10
}
```

The calculation of `unused` has no observable effect.

```text
Before optimization:

    x * 100 ---> unused
    x + 10  ---> return

After optimization:

    x + 10  ---> return
```

The wrapping multiplication can disappear entirely.

### Function inlining

Function calls have some overhead, particularly when the compiler cannot optimize across the function boundary.

```rust
fn double(x: i32) -> i32 {
    x * 2
}

fn calculate(x: i32) -> i32 {
    double(x) + 10
}
```

The compiler may inline `double` into `calculate`.

```text
Before:

 calculate()
      |
      v
  double()
      |
      v
   return
      |
      v
   add 10

After:

 calculate()
      |
      v
    x * 2
      |
      v
   add 10
```

Inlining can also expose opportunities for constant propagation and elimination of redundant instructions.

**However, excessive inlining increases binary size and instruction-cache pressure.** Consequently, LLVM uses heuristics rather than inlining everything.

### Loop optimizations and vectorization

Consider:

```rust
fn add_arrays(a: &[f32], b: &[f32], out: &mut [f32]) {
    for i in 0..out.len() {
        out[i] = a[i] + b[i];
    }
}
```

A straightforward implementation processes one element at a time.

Under suitable conditions, LLVM may use SIMD instructions that process several elements in one instruction.

```text
Scalar execution:

    a[0] + b[0] --> out[0]
    a[1] + b[1] --> out[1]
    a[2] + b[2] --> out[2]
    a[3] + b[3] --> out[3]

Vectorized execution:

    [a0 a1 a2 a3]
          +
    [b0 b1 b2 b3]
          |
          v
    [o0 o1 o2 o3]
```

Vectorization depends on the code, data dependencies, target CPU features, and compiler analysis. **Release mode enables aggressive optimization but does not guarantee vectorization.**

### Bounds-check elimination

Rust performs runtime bounds checks on indexing operations when necessary.

```rust
let value = numbers[index];
```

The compiler may need to verify:

```text
index < numbers.len()?
           |
     +-----+-----+
     |           |
     v           v
    Yes         No
     |           |
     v           v
   Read        Panic
```

When the compiler can prove an index is always valid, it can eliminate the check.

For example, iterating directly over a slice often makes it easier to generate code without redundant indexing checks:

```rust
fn sum(values: &[i64]) -> i64 {
    values.iter().copied().sum()
}
```

**The optimization removes checks proven unnecessary; it does not disable Rust's memory-safety rules.**

## 3. What does `--release` actually enable?

Cargo's default release profile is approximately equivalent to:

```toml
[profile.release]
opt-level = 3
debug = false
debug-assertions = false
overflow-checks = false
lto = false
codegen-units = 16
incremental = false
panic = "unwind"
```

These defaults are not necessarily the optimal settings for every workload.

| Setting                    | Purpose                                                                    |
| -------------------------- | -------------------------------------------------------------------------- |
| `opt-level = 3`            | Enables aggressive compiler optimizations                                  |
| `debug = false`            | Omits debugging information by default                                     |
| `debug-assertions = false` | Disables `debug_assert!` checks                                            |
| `overflow-checks = false`  | Disables automatic integer overflow checks                                 |
| `lto = false`              | Uses limited local link-time optimization rather than full cross-crate LTO |
| `codegen-units = 16`       | Balances compilation parallelism and optimization opportunities            |
| `incremental = false`      | Disables incremental compilation                                           |

**An important subtlety:** **`assert!` remains active in release builds. `debug_assert!` normally does not.**

Integer overflow behavior can also differ. For example, adding `1` to a runtime `u8` value of `255` normally panics in development mode but wraps to `0` in the default release profile. Explicit operations such as `checked_add` and `wrapping_add` provide consistent, intentional semantics across profiles.

## 4. Link-time optimization (LTO)

Normally, functions and dependencies can be compiled in separate units.

This creates an optimization problem: the compiler may not have sufficient visibility to optimize across boundaries.

```text
 Crate A                 Crate B
    |                       |
    v                       v
Compile A               Compile B
    |                       |
    v                       v
 Code A                  Code B
    |                       |
    +-----------+-----------+
                |
                v
              Link
                |
                v
             Binary
```

**Link-Time Optimization allows additional compiler analysis across compilation-unit boundaries, including across crates.**

```text
   Crate A                 Crate B
      |                       |
      v                       v
Intermediate            Intermediate
    Code                    Code
      |                       |
      +-----------+-----------+
                  |
                  v
             Global LLVM
            Optimization
                  |
                  v
            Machine Code
                  |
                  v
               Binary
```

For example, LTO may enable a function from Crate B to be inlined into code in Crate A, exposing further optimization opportunities.

A more aggressive configuration:

```toml
[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
```

Here, `lto = "thin"` enables cross-crate ThinLTO, while `codegen-units = 1` gives the backend more optimization visibility within each crate, typically at the expense of compilation time.

## 5. CPU-specific optimizations

Rust can also instruct LLVM to optimize for a particular CPU.

```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

This allows the compiler to take advantage of supported CPU features, potentially generating more efficient SIMD instructions.

**The trade-off is portability:** a binary compiled for one CPU may use instructions unavailable on another CPU.

## 6. Engineering trade-offs

```text
                  Optimization Level
                           |
         +-----------------+-----------------+
         |                                   |
         v                                   v
  Less aggressive                     More aggressive
         |                                   |
         v                                   v
   Faster builds                       Slower builds
 Easier debugging                    Harder debugging
 Often slower code                   Often faster code
Less compiler work                  More compiler work
```

**There is no guarantee that the highest optimization level produces the fastest program.** More inlining, for example, can increase instruction-cache misses and occasionally reduce performance.

**A practical approach is to start with the default release profile, benchmark realistic workloads, and introduce LTO, fewer code-generation units, or CPU-specific tuning when measurements justify them.**

**The central principle:** Rust's release compiler spends additional time analyzing and transforming code so the CPU can perform less work at runtime. The performance improvement comes from the generated machine instructions, not from a faster Rust runtime.
