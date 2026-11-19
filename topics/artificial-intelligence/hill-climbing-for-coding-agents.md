# Hill climbing for coding agents

In agentic coding, **hill climbing is a prompting technique that makes a coding agent improve an existing implementation through repeated, measurable experiments.**

Rather than expecting the agent to produce an optimal solution on its first attempt, the prompt gives it a process: evaluate the current code, identify a promising improvement, implement it, measure the results, and keep the change only when it makes things better.

The core loop looks like this:

```text
     Initial implementation
               |
               v
     Evaluate current code <---------------+
               |                           |
               v                           |
      Identify a weakness                  |
               |                           |
               v                           |
     Propose a small change                |
               |                           |
               v                           |
       Implement and test                  |
               |                           |
               v                           |
        Did it improve?                    |
               |                           |
     +---------+---------+                 |
     |                   |                 |
    Yes                  No                |
     |                   |                 |
     v                   v                 |
    Keep               Revert              |
     |                   |                 |
     +---------+---------+                 |
               |                           |
               +-- Repeat -----------------+
```

**The coding agent searches through possible implementations and uses feedback to decide what to try next.**

This approach is closely related to iterative refinement and automated code optimization. The prompt guides the search, while tests, benchmarks, or other evaluations determine whether an attempted improvement is worth keeping.

## 1. Ordinary prompting versus hill-climbing prompting

Consider a JSON parser that has become a performance bottleneck.

A conventional coding prompt might be:

> Optimize the JSON parser to make it faster.

The agent will likely inspect the implementation, make some changes, perhaps run the tests, and finish.

The limitation is that the prompt doesn't establish a process for systematically discovering better implementations.

A hill-climbing prompt is more explicit:

**Example hill-climbing prompt**

```text
Optimize the JSON parser using iterative hill climbing.

Objective:
  Minimize median parsing latency.

Constraints:
  - Preserve correctness and public APIs.
  - All existing tests must pass.
  - Do not alter benchmark definitions.

Process:
  1. Measure the current implementation.
  2. Identify one performance bottleneck.
  3. Form a hypothesis.
  4. Make one targeted modification.
  5. Run tests and benchmarks.
  6. Keep the change only if it improves results without breaking correctness. Otherwise revert.
  7. Record results and repeat.

Stop:
  After three unsuccessful experiments or when the budget is exhausted.

Report:
  Best implementation, benchmark results, failed attempts, and remaining limitations.
```

- **Objective:** There's a clear definition of what should improve.
- **Experimentation:** The agent is instructed to test multiple hypotheses rather than settle for its first idea.
- **Measurement:** Decisions depend on benchmark results, not just the agent's assessment of its code.
- **Reversibility:** Unsuccessful changes must be discarded.
- **Termination:** The process has a defined stopping condition.

Hill climbing gives the agent a **feedback-driven optimization strategy**.

## 2. What happens during execution?

Suppose the parser starts with the following performance:

```text
Baseline parser latency: 120 ms
Goal: Minimize latency
```

The agent runs a sequence of experiments. **Each new candidate builds on the best implementation found so far, not necessarily the most recent attempt.**

Here are some hypothetical results:

| Iteration | Proposed change              | Latency | Decision |
| --------- | ---------------------------- | ------- | -------- |
| 0         | Original implementation      | 120 ms  | Baseline |
| 1         | Reduce temporary allocations | 92 ms   | Keep     |
| 2         | Add parallel parsing         | 110 ms  | Revert   |
| 3         | Optimize buffer reuse        | 73 ms   | Keep     |
| 4         | Change string decoding       | 75 ms   | Revert   |

After four experiments, the best implementation achieves 73 ms instead of 120 ms, assuming repeated measurements confirm the improvement and all correctness requirements remain satisfied.

Iteration 2 performed worse than iteration 1. The agent therefore reverted it before beginning iteration 3.

Likewise, iteration 4 wasn't allowed to replace iteration 3 because it performed worse.

**Greedy hill climbing maintains a best-known solution and explores improvements from that state.**

## 3. The three essential components

For a hill-climbing prompt to work well, it needs to specify three things: what counts as improvement, what kinds of changes are allowed, and when a proposed change should be accepted.

### A. An objective function

The agent needs a way to distinguish a better implementation from a worse one.

Different coding tasks naturally require different objectives.

| Objective              | Measurement                                  |
| ---------------------- | -------------------------------------------- |
| Improve runtime        | Benchmark latency                            |
| Reduce memory usage    | Peak RSS or allocated bytes                  |
| Improve correctness    | Passing regression tests                     |
| Reduce code complexity | Measurable complexity constraints and review |
| Reduce inference cost  | Dollars per successful request               |

Sometimes the objective involves several competing qualities.

For example, optimizing performance while preserving correctness is different from simply minimizing execution time.

A parser that becomes 30% faster but starts producing incorrect results is not an improvement.

**The prompt needs to make these constraints explicit rather than leaving the agent to infer them.**

### B. A neighborhood of possible changes

In optimization theory, a **neighborhood** consists of the candidate solutions that can be reached from the current solution.

For agentic coding, the neighborhood corresponds to the changes the agent is allowed or encouraged to investigate.

```text
                  Current code
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
     Change          Change          Change
   algorithm      data layout      allocation
       |               |               |
       v               v               v
  Candidate A     Candidate B     Candidate C
       |               |               |
       +---------------+---------------+
                       |
                       v
                Evaluate changes
```

A prompt might restrict the agent to one conceptual optimization per iteration.

This has a practical advantage: when a benchmark improves, it's easier to determine which change caused the improvement.

However, the neighborhood shouldn't become unnecessarily restrictive.

Some performance problems require architectural changes that cannot be discovered through tiny local modifications.

The tradeoff is between **controlled experimentation and the ability to explore substantially different implementations**.

### C. An acceptance criterion

The simplest acceptance rule is mathematical:

```text
Accept(c') = 1 if Q(c') > Q(c), otherwise 0
```

Here, `c` is the current implementation, `c'` is the candidate implementation, and `Q` is a quality score where higher values are better.

The agent accepts the new implementation only when its measured quality is better.

In real software, the decision is usually more complicated. Correctness must be maintained, measurements may be noisy, and performance improvements must be large enough to distinguish from normal benchmark variability.

A useful acceptance policy is therefore:

**Keep a change only when it passes all correctness checks and demonstrates a reproducible improvement against the chosen objective.**

## 4. Hill climbing versus self-refinement

Self-refinement asks a large language model (LLM) to critique and revise its own code.

```text
Generate implementation
           |
           v
Critique implementation <-------------+
           |                          |
           v                          |
 Rewrite implementation               |
           |                          |
           +-- Repeat ----------------+
```

The agent produces a solution, evaluates it conceptually, and attempts to improve it.

This can help with code readability, identifying edge cases, or finding design problems.

Hill-climbing prompting introduces a stronger feedback mechanism:

```text
   Generate implementation
              |
              v
       Run verification
              |
              v
     Propose improvement
              |
              v
    Run verification again
              |
              v
Compare with best-known result
              |
              v
        Keep or revert
```

**The agent keeps a revision only if it demonstrates improvement against a defined criterion.**

Executable tests and benchmarks can provide more reliable evidence than the model's own judgment about the quality of its implementation.

## 5. Why hill climbing works particularly well for coding agents

Many software engineering tasks have an advantage that more subjective problems don't: **the result can be tested automatically**.

A coding agent can directly interact with the development environment to:

- Modify the implementation.
- Compile the project.
- Execute unit and integration tests.
- Run benchmarks.
- Examine profiler output.
- Revert unsuccessful changes using version control.

That makes it possible to construct an optimization loop with relatively little manual intervention.

Performance optimization is a particularly natural application. The agent can repeatedly test algorithmic improvements, memory allocation strategies, or data structure choices against measurable outcomes.

The same idea can be applied to improving test coverage, simplifying code under explicit constraints, or reducing inference costs.

However, hill climbing has limitations.

A coding agent can become trapped in a local optimum where small modifications no longer help, even though a completely different architecture might produce a much better result.

It can also overfit to a benchmark, optimize the wrong metric, or exploit weaknesses in the evaluation process. **That is why tests, benchmarks, and acceptance constraints need to remain independent of the implementation being optimized.**

## 6. The deeper engineering principle

A traditional coding prompt essentially asks:

> What implementation should solve this problem?

A hill-climbing prompt instead asks:

> Given the current implementation and the available measurements, what experiment is most likely to produce a meaningful improvement?

The agent's work becomes a cycle of hypotheses and evidence:

```text
 Hypothesis <--------------------+
     |                           |
     v                           |
Code change                      |
     |                           |
     v                           |
Measurement                      |
     |                           |
     v                           |
  Evidence                       |
     |                           |
     v                           |
  Decision                       |
     |                           |
     +-- New hypothesis ---------+
```

The agent improves the implementation over successive attempts by proposing experiments, executing them correctly, interpreting their results, and preserving improvements.

The quality of the process depends on the objective being optimized, the range of experiments the agent can explore, and the reliability of the feedback.

**Hill climbing turns a coding prompt from a request for an implementation into instructions for an iterative, evidence-driven search for a better implementation.**
