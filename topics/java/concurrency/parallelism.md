# Parallelism

While concurrency is the **composition** of independent processes, parallelism
is the simultaneous **execution** of those processes.

In a parallel system, multiple tasks happen at the exact same physical instant.
This requires hardware with multiple processing units: a multi-core CPU, a GPU,
or a cluster of networked computers.

## Concurrency vs parallelism

| Feature       | Concurrency                     | Parallelism                        |
|---------------|---------------------------------|------------------------------------|
| **Execution** | Interleaved (switching between) | Simultaneous (running together)    |
| **Hardware**  | Can run on a single core        | Requires multiple cores/processors |
| **Goal**      | Responsiveness and structure    | Computational speed and throughput |
| **Metaphor**  | One juggler with many balls     | Multiple jugglers with many balls  |

## Types of parallelism

### Data parallelism

The same operation is performed on different subsets of a large data set. This
is the foundation of high-performance computing and machine learning.

To brighten an image, the system splits the image into four quadrants and sends
each to a different CPU core to apply the same brightness formula. Modern GPUs
are the kings of data parallelism, using thousands of small cores to process
pixels or matrix values simultaneously.

### Task parallelism

Different tasks—which may perform entirely different operations—run across
multiple processing units.

On a modern smartphone, one core handles the cellular radio's background data,
another renders the UI of a game, and a third decodes an MP3 file. These tasks
progress truly independently in time.

## Amdahl's Law

A common misconception is that doubling processors doubles speed. The speedup is
limited by the **sequential fraction**—parts of the code that cannot be
parallelized (like initialization or final data aggregation).

$$S = \frac{1}{(1-p) + \frac{p}{s}}$$

- $S$ is the theoretical speedup of the whole task
- $p$ is the proportion that can be made parallel
- $s$ is the speedup of the parallel portion

If 10% of your program must remain sequential, maximum possible speedup is 10x,
even with 1,000,000 cores.

## Instruction-level parallelism

Even within a single CPU core, parallelism exists at the hardware level.

**Pipelining:** Like an assembly line, the CPU starts the "fetch" phase of the
next instruction before the "execute" phase of the current one finishes.

**Superscalar execution:** The CPU can execute multiple instructions (like an
addition and a memory load) in the same clock cycle if they don't depend on each
other.
