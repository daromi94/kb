# AOT compilation

**Ahead-of-Time (AOT) compilation** means that a program's source code is translated into machine code **before the program starts executing**, rather than compiling it during execution.

Rust uses this compilation model by default.

## 1. How Rust compilation works

Consider a simple Rust program:

```rust
fn main() {
    let x = 10;
    let y = 20;
    println!("{}", x + y);
}
```

When the Rust compiler (`rustc`) processes this program, it generates a native executable containing machine instructions for the target CPU architecture.

```text
    Source Code
      main.rs
         |
         v
+----------------+
|  Rust Compiler |
|      rustc     |
+----------------+
         |
         | Parse
         | Type checking
         | Borrow checking
         | Optimization
         | Code generation
         |
         v
   Machine Code
         |
         v
+----------------+
|  Native Binary |
|     program    |
+----------------+
         |
         | Execute
         v
+----------------+
|       CPU      |
+----------------+
```

The crucial property is that **compilation and execution are separate activities**.

For example:

```bash
rustc main.rs

./main
```

The first command compiles the program.

The second executes the already-compiled binary.

**The CPU executes native instructions without needing the Rust compiler.**

## 2. AOT vs. JIT compilation

There are two important compilation models.

### Ahead-of-Time (AOT)

Rust, C, and C++ commonly use AOT compilation.

```text
BUILD TIME                         RUNTIME

  Rust Source Code
          |
          v
      Compiler
          |
          v
    Native Binary
          |
          +------------------------------+
                                         |
                                         v
                                   CPU Executes
                                   Machine Code
```

**Most compilation and optimization decisions happen before execution.**

### Just-in-Time (JIT)

Java's HotSpot JVM commonly combines bytecode interpretation and JIT compilation.

```text
BUILD TIME                                   RUNTIME

     Java Source
          |
          v
        javac
          |
          v
      Bytecode
          |
          +-------------------------------------+
                                                |
                                                v
                                               JVM
                                                |
                                   +------------+------------+
                                   |                         |
                                   v                         v
                              Interpreter              JIT Compiler
                                   |                         |
                                   |                         v
                                   |                   Machine Code
                                   |                         |
                                   +------------+------------+
                                                |
                                                v
                                          CPU Executes
```

The JVM can observe which methods are executed frequently and compile them into optimized machine code while the application runs.

This is an important difference.

**Rust's compiler optimizes using information available at build time. A JIT can additionally optimize using information collected during execution.**

For example, a JIT might observe that a method consistently receives objects of a particular type and generate specialized machine code, guarded by checks that allow deoptimization if the assumption stops holding.

Rust generally doesn't perform this kind of runtime profiling and recompilation automatically.

## 3. Performance implications

AOT compilation offers several advantages, but also introduces trade-offs.

| Characteristic          | Rust (AOT)                                    | Java HotSpot (JIT)                        |
| ----------------------- | --------------------------------------------- | ----------------------------------------- |
| Native code generation  | Before execution                              | During execution                          |
| Startup                 | Typically fast                                | May involve JVM initialization and warmup |
| Runtime compiler        | Generally unnecessary                         | Part of JVM                               |
| Runtime profiling       | Not required for normal execution             | Used for adaptive optimization            |
| Optimization knowledge  | Static analysis and optional offline profiles | Static analysis and runtime profiles      |
| Runtime memory overhead | Usually lower                                 | Includes JVM and JIT infrastructure       |

**An important distinction:** **AOT compilation does not automatically make Rust faster than Java.**

JIT compilation can sometimes produce better optimized code because it knows how the program actually behaves.

Conversely, AOT compilation avoids spending CPU cycles compiling application methods while the program is running.

## 4. What happens inside Rust's compiler?

Rust's compilation pipeline contains several intermediate representations.

A simplified view:

```text
   Rust Source
        |
        v
  Parsing / AST
        |
        v
 Macro Expansion
        |
        v
       HIR
        |
        | Type checking
        v
       MIR
        |
        | Borrow checking
        | MIR transformations
        v
Monomorphization
        |
        v
LLVM IR (default)
        |
        | Optimization
        v
  Machine Code
        |
        v
     Linker
        |
        v
Native Executable
```

Some important concepts:

**HIR (High-level Intermediate Representation)** represents the program in a form suitable for semantic analysis.

**MIR (Mid-level Intermediate Representation)** provides a simpler control-flow representation used for borrow checking and compiler transformations.

**Monomorphization** generates concrete implementations of generic functions for the types used by the program.

**LLVM** is Rust's default production compiler backend. It performs machine-level optimizations and emits machine code.

**Linking** combines compiled object files and required libraries into an executable or library.

All of these operations normally happen before the program executes.

## 5. Does AOT mean everything is decided at compile time?

No.

**AOT compilation does not eliminate runtime decisions.**

A Rust program can still perform dynamic dispatch, allocate memory, create threads, communicate over networks, load shared libraries, and make decisions using runtime data.

For example:

```rust
fn calculate(x: i32) -> i32 {
    if x > 100 {
        x * 2
    } else {
        x + 10
    }
}
```

The compiler generates machine code implementing the conditional logic, but the branch taken depends on the value of `x` at runtime.

```text
     Compile Time
           |
           v
 Generate machine code
for both possibilities
           |
           v
        Runtime
           |
           v
     Read x value
           |
           v
       x > 100?
     +-----+-----+
     |           |
     v           v
    Yes         No
     |           |
     v           v
    x*2        x+10
```

The distinction is between **when instructions are generated** and **when those instructions make decisions**.

## 6. The most important engineering trade-off

**AOT compilation shifts computational work from runtime to build time.**

```text
           AOT
            |
            v
 More work during builds
            |
            v
   Less compiler work
    during execution


           JIT
            |
            v
 Less native compilation
    before execution
            |
            v
   Runtime compilation
and adaptive optimization
```

This helps explain several Rust characteristics:

- **Compilation can be relatively expensive**, especially with extensive generics and optimizations.
- **Startup performance is generally strong**, since no JIT warmup is required.
- **Runtime behavior can be more predictable**, because there is no conventional JIT compiler activating during execution.
- **The compiler can catch many errors before execution**, although this is primarily a consequence of Rust's type system and borrow checker, not AOT compilation itself.

### Key takeaway

**AOT describes when compilation happens, not how fast the resulting program necessarily runs.**

Rust generates native machine code before execution, allowing the resulting program to run without a Rust compiler or language virtual machine. That is one important reason Rust is well suited to operating systems, embedded software, performance-sensitive services, and low-level systems programming.
