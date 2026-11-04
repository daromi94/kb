# Agentic verification

AI agents are becoming increasingly capable of writing software. They can implement features, fix bugs, refactor code, and even build entire applications with relatively little human intervention.

But there is a fundamental problem:

**Producing code is not the same as proving that the code works.**

As AI reduces the cost of writing software, the engineering bottleneck shifts toward verification: establishing sufficient evidence that an implementation behaves correctly, satisfies its requirements, and is safe to deploy.

Agentic verification addresses this problem by giving AI agents the ability to execute, observe, test, and validate their own work, rather than relying exclusively on human inspection.

## 1. What is agentic verification?

Agentic verification is an engineering approach in which AI agents use executable feedback mechanisms to evaluate their work and iteratively correct problems.

Rather than generating a solution and declaring it complete, the agent participates in a continuous feedback loop.

```text
                Requirements
                      |
                      v
                  AI Agent
                      |
                      v
              Generate solution
                      |
                      v
            Execute verification <----------------------+
                      |                                 |
                      v                                 |
              Collect evidence                          |
                      |                                 |
                      v                                 |
            Evaluate correctness                        |
                      |                                 |
      +---------------+---------------+                 |
      |                               |                 |
      v                               v                 |
    PASS                            FAIL                |
      |                               |                 |
      v                               v                 |
Review result                  Diagnose issue           |
      |                               |                 |
      v                               v                 |
   Deliver                     Modify solution          |
                                      |                 |
                                      v                 |
                                Verify again            |
                                      +-----------------+
```

The essential distinction is that the agent doesn't merely reason about whether a solution should work. It interacts with an execution environment that provides actual evidence.

For example, a coding agent implementing an HTTP endpoint could:

1. Generate the endpoint implementation.
2. Compile the application.
3. Start the server.
4. Send real HTTP requests.
5. Validate responses against expected behavior.
6. Inspect logs and traces for errors.
7. Correct problems and repeat the process.

This resembles the traditional engineering cycle of implementation, testing, and debugging, except that the agent automates much of the iteration.

The core principle is:

An agent should have a way to observe whether its actions achieved the intended result.

## 2. The shift from code generation to verification

Historically, software development involved two expensive activities:

- Construction: Designing and implementing the system.
- Verification: Determining whether the implementation satisfies its requirements.

AI agents dramatically reduce the time needed for construction.

However, faster code generation does not automatically reduce the complexity of verifying correctness.

Consider a distributed caching system.

An agent might generate a complete cache implementation in minutes.

But important questions remain:

- Does the cache preserve the required consistency guarantees?
- Can concurrent updates produce stale values?
- What happens if a node crashes during invalidation?
- Does the implementation behave correctly during network partitions?
- Does the cache actually improve performance under realistic workloads?

Generating the implementation and answering these questions are fundamentally different problems.

```text
Traditional development
-----------------------

Implementation:  High effort
Verification:    High effort


Agent-assisted development
--------------------------

Implementation:  Lower effort
Verification:    Still requires strong evidence
```

This changes where engineering attention should be invested.

Instead of exclusively improving the speed of code generation, systems should be designed to make correctness observable and automatically testable.

## 3. Verification requires an oracle

One of the most important ideas in software testing is the concept of a test oracle.

A test oracle is a mechanism for determining whether an observed result is correct.

Suppose a function returns:

```text
Input:  [5, 2, 8, 1]
Output: [1, 2, 5, 8]
```

The function produced an output, but how can an agent establish that it is correct?

It needs something against which to compare the result.

That might be an expected output, an invariant, a trusted reference implementation, or a formal specification.

```text
            Input
              |
              v
       Implementation
              |
              v
        Actual output
              |
              v
     Compare with oracle
              |
  +-----------+-----------+
  |                       |
  v                       v
Match                 Mismatch
  |                       |
  v                       v
PASS                    FAIL
```

Without an oracle, an agent can execute code and observe the output, but it cannot reliably establish correctness.

This is particularly important because language models are good at producing plausible explanations.

An agent saying "the implementation appears correct" is not equivalent to a test demonstrating that a property holds.

The effectiveness of agentic verification therefore depends heavily on the quality of its verification oracles.

## 4. The major techniques for agentic verification

Different techniques establish different properties of software.

No single verification mechanism can prove everything about a sufficiently complex system.

### A. End-to-end verification

End-to-end (E2E) testing validates observable behavior through the interfaces of a running system.

Consider a web application that creates orders.

```text
HTTP request
      |
      v
API Gateway
      |
      v
Order Service
      |
      v
Database
      |
      v
HTTP response
      |
      v
Verify outcome
```

A unit test might prove that an order creation method invokes its dependencies correctly.

An E2E test can establish that a real request produces the expected persisted order and response.

For AI agents, this is particularly valuable because integration failures are not always visible from source code.

An agent may successfully compile a program while accidentally breaking routing, authentication, persistence, or configuration.

By interacting with the actual application, the agent gains feedback about system-level behavior.

The limitation is that E2E tests tend to be slower, more expensive, and sometimes less deterministic than unit tests.

### B. Property-based verification

Traditional tests often validate known examples.

Property-based testing instead validates general properties that should hold across many generated inputs.

Consider a concurrent queue.

An important invariant is that an item successfully removed from the queue must have been previously inserted, and cannot be removed twice.

A property-based testing system can generate sequences of operations:

```text
enqueue(A)
enqueue(B)
dequeue() -> A
enqueue(C)
dequeue() -> B
dequeue() -> C
```

It can then validate the required properties.

For concurrent queues, sequential tests alone are not enough. Concurrency testing must also exercise overlapping operations and verify the required concurrency semantics, such as linearizability.

The advantage of property-based testing is that it explores cases beyond a small set of manually chosen examples.

This is valuable for agents because it reduces dependence on the examples the agent happened to anticipate.

### C. Differential verification

Differential testing compares an implementation against another implementation that acts as a reference.

This is especially useful for migrations, rewrites, or optimizations.

Imagine replacing a query execution engine.

```text
                 Query
                   |
     +-------------+-------------+
     |                           |
     v                           v
Old engine                  New engine
     |                           |
     v                           v
 Result A                    Result B
     |                           |
     +-------------+-------------+
                   |
                   v
            Compare results
                   |
                   v
         Equivalent behavior?
```

An agent can execute thousands of queries against both implementations and compare the results.

This can reveal subtle behavioral differences involving null handling, numeric precision, ordering, and edge cases.

The important assumption is that the reference implementation provides a trustworthy behavioral baseline. If both implementations contain the same bug, differential testing may not detect it.

### D. Performance verification

Correctness isn't always purely functional.

For performance-sensitive systems, latency, throughput, memory usage, and resource consumption may be essential requirements.

Suppose an agent optimizes a serialization routine.

The implementation produces identical output, but performance still needs to be established.

A verification process might measure:

| Property               | Verification                        |
| ---------------------- | ----------------------------------- |
| Functional correctness | Reference output comparison         |
| Throughput             | Representative throughput benchmark |
| Tail latency           | p95/p99 latency under load          |
| Allocations            | Allocation profiling                |
| CPU consumption        | CPU profiling                       |
| Memory usage           | Peak and steady-state measurements  |

Performance results must be compared under controlled conditions. A faster benchmark is not meaningful if the new implementation was tested under a different workload or with a different environment.

## 5. Verification loops are only as good as their feedback

It might seem that giving an agent a large test suite solves the correctness problem.

Unfortunately, it doesn't.

An important failure mode arises when an agent implements both the functionality and the tests based on the same incorrect assumption.

Imagine a rate limiter intended to enforce a global limit of 1,000 requests per second across a cluster.

The agent incorrectly implements a per-node limit of 1,000 requests per second.

It then writes tests that validate each node independently.

All tests pass.

But with five nodes, the cluster could admit approximately 5,000 requests per second.

The agent has verified the implementation against an incorrect understanding of the requirement.

```text
             Actual requirement
                      |
                      X
              Misunderstanding
                      |
       +--------------+--------------+
       |                             |
       v                             v
Implementation                     Tests
       |                             |
       +--------------+--------------+
                      |
                      v
                  All green
                      |
                      v
               Still incorrect
```

This is an example of a **correlated verification failure**.

The implementation and the verification logic share the same mistaken assumption.

Adding more tests based on that assumption doesn't necessarily increase confidence.

This is why independently established requirements, invariants, reference implementations, and external behavior are so valuable.

The objective is not to maximize the number of passing tests.

It is to maximize meaningful evidence of correctness.

## 6. The role of independent verification

A useful approach for complex agent workflows is separating implementation from verification.

For example:

```text
                    Specification
                          |
          +---------------+---------------+
          |                               |
          v                               v
Implementation Agent             Verification Agent
          |                               |
          v                               v
    Produces code                  Designs checks
          |                               |
          +---------------+---------------+
                          |
                          v
                   Execute checks
                          |
                          v
                   Review evidence
```

The verification agent evaluates the work against independently defined requirements, rather than merely accepting the implementation agent's explanation of what it built.

This can reduce certain biases.

However, using a second agent does not guarantee independence.

If both agents receive the same incorrect specification, they may reach the same incorrect conclusion.

And if the verification agent merely reviews the implementation agent's summary, it may inherit the same assumptions.

Meaningful independence comes from the verification method and evidence, not simply the number of agents involved.

## 7. The verification environment becomes part of the architecture

One of the most useful implications is that software systems should be built to support automated verification.

A good environment for agentic development provides agents with:

- Reproducible build and test commands.
- Deterministic test environments where feasible.
- Access to logs, traces, metrics, and diagnostic output.
- Representative test data and realistic workloads.
- Clear behavioral contracts and invariants.
- Controlled ways to interact with running applications.

This makes the system easier for agents to work on and easier for engineers to maintain.

Consider the difference between two systems.

- **System A:** The application requires extensive manual setup, failures are difficult to reproduce, and successful operation is established mainly by human observation.
- **System B:** The application can run in a reproducible environment, exposes useful diagnostics, and has executable tests for its important behaviors.

Agents can operate much more effectively in System B.

The reason is straightforward: the environment provides shorter and more reliable feedback loops.

This leads to an important architectural principle:

Design for verifiability, not merely implementability.

## 8. Verification must be risk-aware

Not every change requires the same depth of verification.

A small documentation change and a modification to a distributed consensus algorithm have very different failure consequences.

Verification effort should reflect the criticality, complexity, and reversibility of the change.

| Change               | Appropriate verification                                      |
| -------------------- | ------------------------------------------------------------- |
| Simple formatting    | Linting, visual checks                                        |
| Pure function        | Unit and property-based tests                                 |
| API modification     | Contract and integration tests                                |
| Database migration   | Differential testing, migration rehearsals, rollback checks   |
| Concurrent algorithm | Concurrency stress tests, invariants, possibly model checking |
| Distributed protocol | Fault injection, model checking, recovery testing             |

For distributed systems, normal-path tests are particularly insufficient.

A protocol may behave correctly when all nodes and networks are healthy while failing under message reordering, partial failures, or concurrent membership changes.

Verification must explore the failure models that matter.

## 9. What agentic verification cannot solve

Even excellent automated verification has fundamental limitations.

First, verification cannot establish that the wrong requirements are correct.

An agent may perfectly implement a feature that should never have been built.

Second, tests cannot generally establish the absence of all possible bugs.

They provide evidence over specific behaviors, input spaces, and environmental conditions.

Third, verification systems can themselves be flawed.

A defective test oracle may accept incorrect behavior or reject correct behavior.

Finally, passing checks cannot replace engineering judgment about trade-offs, operational risk, usability, and whether the system solves the intended problem.

This is why the most useful output of agentic verification is not simply a success message.

It is a body of evidence that can be evaluated.

A useful completion report distinguishes:

```text
VERIFIED
--------
- Code compiles
- Unit tests pass
- API contract tests pass
- Required invariants hold for tested cases
- Benchmark meets defined threshold

NOT VERIFIED
------------
- Behavior during network partitions
- Large-scale production workloads
- Recovery after partial disk failure

ASSUMPTIONS
-----------
- Database provides expected isolation
- External API preserves response semantics
```

That report is substantially more valuable than "Implementation complete; all tests passed."

## 10. The deeper engineering principle

Agentic verification changes the role of automation in software development.

Instead of automation being limited to implementing solutions, agents can participate in establishing evidence that the solutions work.

But there is an important distinction:

Agents can automate the verification process without automatically solving the problem of knowing what should be verified.

Deciding what constitutes correctness requires understanding the requirements, the architecture, the failure modes, and the consequences of being wrong.

That is particularly relevant in complex systems where correctness includes properties such as consistency, isolation, fault tolerance, performance, and recoverability.

The resulting engineering workflow becomes:

```text
Define correctness
      |
      v
Specify invariants
      |
      v
Build verification oracles
      |
      v
Delegate execution
      |
      v
Collect measurable evidence
      |
      v
Evaluate remaining risk
      |
      v
Ship or iterate
```

The central lesson is that the value of AI agents comes not only from generating code faster, but from making the entire engineering process more evidence-driven.

A system that enables agents to implement, execute, observe, and validate their changes can achieve much higher development velocity.

But that velocity is sustainable only when the evidence supporting correctness keeps pace with the code being produced.

The goal is not to build agents that always say their work is correct. It is to build agents that can demonstrate what is correct, explain what remains unverified, and provide enough evidence to support responsible engineering decisions.
