# Critical thinking with AI agents

AI agents are fundamentally changing how software engineering happens. Tasks that previously required hours of investigation, implementation, debugging, and testing can increasingly be delegated to agents that complete much of the work autonomously.

But this introduces an interesting problem:

When the cost of producing software approaches zero, the ability to evaluate software becomes increasingly important.

The challenge is no longer exclusively about writing correct code. It is about determining whether the right problem was solved, whether the solution is appropriate, and whether the evidence supporting its correctness is sufficient.

This is where critical thinking becomes essential.

## 1. What is critical thinking?

Critical thinking is the disciplined process of evaluating information, assumptions, arguments, and evidence before accepting a conclusion.

In software engineering, it means asking questions such as:

- Are we solving the right problem?
- What assumptions does this solution depend on?
- What evidence supports the proposed approach?
- What alternatives were considered?
- Under what conditions would this solution fail?
- What does correctness actually mean here?

Consider an application experiencing high request latency.

An engineer asks an AI agent to investigate the problem. The agent examines the code and recommends increasing the thread pool size.

Without critical thinking, the recommendation might be accepted because it sounds technically reasonable.

With critical thinking, the recommendation becomes a hypothesis:

> Increasing thread pool capacity may improve throughput if insufficient concurrency is the bottleneck.

Now the important questions emerge.

Does the service have enough CPU capacity? Is the workload CPU-bound or I/O-bound? Are requests spending time waiting on locks? Is the bottleneck actually a downstream dependency?

The difference is fundamental:

A plausible explanation is not necessarily a correct explanation.

Critical thinking transforms a convincing answer into a testable claim.

## 2. The spectrum: Cognitive offloading, deferral, and surrender

Delegating work to AI is not inherently problematic. The real issue is how much ownership of the reasoning is retained.

There are three important levels.

```text
COGNITIVE OFFLOADING
--------------------
Agent performs the work
Human evaluates evidence
Human owns the decision
        |
        v
COGNITIVE DEFERRAL
------------------
Agent produces an answer
Answer becomes an assumption
Independent scrutiny decreases
        |
        v
COGNITIVE SURRENDER
-------------------
Agent produces an answer
Answer is accepted as truth
Understanding is no longer required
```

### Cognitive offloading

Cognitive offloading means delegating execution while maintaining ownership of the result.

For example, an agent could:

1. Investigate a performance regression.
2. Collect profiling information.
3. Identify possible bottlenecks.
4. Propose optimizations.
5. Run benchmarks.

The engineer still evaluates whether the evidence supports the proposed optimization.

This is generally a productive use of agents.

### Cognitive deferral

Cognitive deferral occurs when the agent's output quietly becomes an assumption for subsequent work.

For example, an agent claims that a particular component is thread-safe. Another agent uses that claim to implement concurrency-sensitive functionality.

Neither verifies the original assumption.

The problem isn't necessarily that the initial answer was wrong. It is that an unverified conclusion has become part of the system's foundations.

### Cognitive surrender

Cognitive surrender occurs when the agent's output is accepted without meaningful evaluation or understanding.

Imagine an agent implementing a distributed locking mechanism.

The implementation compiles, tests pass, and the code looks reasonable.

However, nobody can explain what happens when:

- A lock holder crashes.
- A network partition occurs.
- A lease expires while work is still executing.
- Two processes temporarily believe they own the same resource.

The code exists, but the engineering understanding behind it does not.

This is particularly dangerous because sophisticated AI outputs can appear convincing even when they contain subtle errors.

## 3. Cognitive debt: Software that works but nobody understands

Traditional technical debt occurs when implementation choices create future maintenance costs.

AI-assisted development introduces another kind of debt: cognitive debt.

Cognitive debt accumulates when a system grows faster than the ability to understand its behavior and underlying decisions.

Consider:

```text
  Traditional development                Agent-driven development
  -----------------------                ------------------------

    Understand problem                       Describe problem
             |                                       |
             v                                       v
      Design solution                   Agent designs + implements
             |                                       |
             v                                       v
      Implement code                       Agent tests + debugs
             |                                       |
             v                                       v
      Test and debug                      Working implementation
             |                                       |
             v                                       v
Understand resulting system               Limited understanding?
```

The danger is that an implementation may look complete while the mental model required to maintain it is missing.

This can manifest as two related forms of debt.

Comprehension debt occurs when code exists but the reasoning necessary to modify or troubleshoot it has been lost.

Intent debt occurs when the goals, constraints, and rationale behind implementation decisions are unclear.

For example, an agent might introduce a cache with a five-minute expiration policy.

The implementation works, but several questions remain:

- Why five minutes?
- What consistency guarantees are expected?
- Was stale data considered acceptable?
- What happens during cache invalidation?
- Was the expiration policy a requirement or an assumption?

A future engineer might spend considerably more time recovering this reasoning than the agent spent implementing the feature.

Importantly, maintaining a complete mental model of a large system is neither realistic nor necessary. What matters is preserving the ability to reconstruct the relevant understanding when needed, including knowing which assumptions require verification.

## 4. Critical thinking begins before the agent starts working

A common mistake in agent-driven workflows is treating problem formulation as something the agent should do entirely.

Consider this instruction:

> Improve the performance of the API.

The request leaves fundamental questions unanswered.

What performance characteristic needs improvement? Throughput? Median latency? Tail latency? Resource consumption?

What workload matters? What constraints must be preserved?

An agent can fill in these gaps, but its choices may not match the intended outcome.

A stronger approach begins with a hypothesis and an explicit definition of success.

For example:

> The API's p99 latency increases significantly when concurrent requests exceed 500. Investigate whether database connection pool contention is responsible. Preserve existing consistency guarantees and validate any optimization using representative load tests.

This changes the entire workflow.

```text
        Problem observation
                 |
                 v
       Formulate hypothesis
                 |
                 v
        Define constraints
                 |
                 v
    Establish success criteria
                 |
                 v
         Delegate to agent
                 |
                 v
         Evaluate evidence
                 |
   +-------------+-------------+
   |                           |
   v                           v
Confirm                     Reject
   |                           |
   v                           v
Decide                  New hypothesis
                               |
                               v
                          Investigate
```

A hypothesis need not be correct initially. Its purpose is to establish an explanation that evidence can confirm or reject.

Without one, a polished agent response can anchor thinking around the first plausible explanation.

This is why problem formulation is itself a critical engineering skill.

## 5. Verification is not the same as understanding

One of the most important changes introduced by coding agents is that producing verification artifacts has become much cheaper.

An agent can write tests, run them, detect failures, modify code, and repeat the process autonomously.

That is valuable.

But it creates a subtle trap: confusing successful verification checks with proof of overall correctness.

Consider a distributed rate limiter.

An agent implements a token bucket and produces 30 passing unit tests.

The tests confirm that tokens are added correctly, requests consume tokens, and requests are rejected when capacity is exhausted.

But what if the implementation has a concurrency race?

Or what if time calculations are incorrect when the system clock changes?

Or what if separate instances enforce limits independently when the requirement calls for a global limit?

The tests may all pass while the system violates its actual requirements.

```text
               REQUIREMENTS
                     |
                     v
              Implementation
                     |
                     v
                   Tests
                     |
                     v
                 All green
                     |
                     v
            What was verified?
                     |
       +-------------+-------------+
       |                           |
       v                           v
Tested behavior            Untested behavior
       |                           |
       v                           v
Evidence exists              Unknown risk
```

The important questions are therefore:

What did the test prove? What did it not prove?

This is a fundamental distinction between verification and critical thinking.

Verification provides evidence about specific properties. Critical thinking evaluates whether those properties are sufficient to justify the conclusion.

A strong workflow defines the meaning of verified before implementation, rather than accepting whatever checks the agent happens to produce afterward.

## 6. The orchestration tax: More output does not mean more productivity

Agents can generate work much faster than humans can meaningfully review it.

Imagine several agents working simultaneously:

```text
Agent A ---> Feature implementation --------+
                                            |
Agent B ---> Performance optimization ------+
                                            |
Agent C ---> Refactoring -------------------+---> Review
                                            |        |
Agent D ---> Bug fixes ---------------------+        v
                                            |   Bottleneck
Agent E ---> Test generation ---------------+
```

Increasing the number of agents increases the amount of generated output.

But it does not automatically increase the capacity to evaluate that output.

The difference between work produced and work that can be responsibly reviewed is the orchestration tax.

This becomes especially important when agents make hundreds of small decisions:

- Which defaults to select.
- Which edge cases to ignore.
- Which dependencies to introduce.
- Which architectural patterns to follow.
- Which requirements to reinterpret.

A code review that examines only formatting, structure, and passing tests may miss those decisions entirely.

The solution is not necessarily to review every generated line manually. It is to improve the verification process, surface consequential assumptions, and direct human attention toward the highest-risk decisions.

For instance, agents can be required to provide:

- A summary of architectural decisions and assumptions.
- Evidence supporting correctness.
- Tests performed and properties not covered.
- Known limitations and unresolved risks.

The goal is to reduce review effort without reducing accountability.

## 7. Critical thinking means actively searching for disconfirming evidence

A powerful technique is to ask:

What would have to be true for this solution to be wrong?

Suppose an agent recommends replacing a synchronized queue with a lock-free implementation to improve throughput.

The recommendation sounds reasonable: lock-free algorithms can reduce certain forms of contention.

But a critical evaluation examines alternative explanations.

Maybe the synchronized queue isn't actually the bottleneck.

Maybe contention is low.

Maybe the performance problem comes from cache-line bouncing rather than blocking.

Maybe the lock-free implementation introduces retry overhead that performs worse under the actual workload.

Rather than asking the agent to defend its recommendation, the task becomes discovering conditions under which it fails.

A useful reasoning cycle is:

```text
Proposed explanation
        |
        v
Identify assumptions
        |
        v
Develop counterarguments
        |
        v
Design discriminating tests
        |
        v
Collect evidence
        |
        v
Revise understanding
```

This is closely related to scientific reasoning.

The objective is not to prove an initial idea correct. It is to develop an increasingly accurate understanding of reality.

## 8. Engineering judgment becomes more important, not less

As agents become better at implementation, the distribution of engineering effort changes.

Traditionally, substantial effort was invested between understanding a task and delivering a solution.

With agents, much of that execution can be delegated.

The human contribution increasingly concentrates at the beginning and end.

```text
ENGINEERING WORKFLOW

BEFORE EXECUTION
----------------
What problem matters?
Why does it matter?
What are the constraints?
What would success mean?
        |
        v
AGENT EXECUTION
---------------
Investigate
Implement
Test
Iterate
        |
        v
AFTER EXECUTION
---------------
Is the evidence sufficient?
What assumptions were made?
What remains uncertain?
Is the outcome acceptable?
Who is accountable?
```

This requires strong engineering judgment.

For example, an agent may be exceptionally good at implementing a caching layer.

But deciding whether a caching layer should exist requires understanding the trade-offs between latency, consistency, cost, operational complexity, and maintainability.

Those are not merely implementation questions.

They are product and architecture decisions.

Even if agents eventually become better at evaluating many of these trade-offs, accountability for shipping a system remains a separate concern.

## 9. Keeping critical thinking sharp

Critical thinking requires deliberate practice, particularly when tools make it easy to skip difficult reasoning.

Several habits are especially valuable.

| Habit                               | Why it matters                                                     |
| ----------------------------------- | ------------------------------------------------------------------ |
| Form a hypothesis before delegating | Prevents automatically adopting the agent's first explanation      |
| Ask for counterarguments            | Exposes assumptions and alternative explanations                   |
| Define success criteria upfront     | Prevents redefining success around whatever the agent produces     |
| Inspect verification evidence       | Separates claims of correctness from demonstrated behavior         |
| Review decisions, not just diffs    | Surfaces architectural and product trade-offs                      |
| Practice important skills manually  | Maintains the ability to supervise and challenge agents            |
| Reconstruct understanding on demand | Avoids unnecessary memorization without surrendering comprehension |

These practices should be proportional to risk.

Choosing a low-stakes configuration or producing a disposable prototype does not require the same level of scrutiny as modifying a financial transaction system or changing a distributed consensus protocol.

The goal is not to maximize skepticism toward every agent output.

It is to maintain an appropriate level of scrutiny for the consequences of being wrong.

## 10. The deeper principle: Offload execution, not accountability

The core insight is that an engineer's value is not simply the amount of code produced.

It is the ability to understand problems, evaluate alternatives, make informed trade-offs, and take responsibility for the resulting system.

AI agents can accelerate investigation, implementation, and even significant portions of verification.

But faster output does not automatically produce better decisions.

Consider the difference between two outcomes:

- **Outcome A:** An agent produces a working solution, tests pass, and it is shipped without anyone understanding its important assumptions.
- **Outcome B:** An agent produces the same solution, but the relevant assumptions are explicit, the verification evidence is understood, and the architectural trade-offs are defensible.

Both may produce identical code.

The difference is the quality of engineering judgment surrounding that code.

And that difference becomes especially important when the system fails, requirements change, or a surprising edge case appears in production.

The central principle is therefore:

**Delegate as much implementation as makes sense, but preserve the ability to explain the important decisions, challenge the evidence, and take responsibility for what ships.**

The future of engineering is not simply about producing more software with fewer keystrokes. It is about making better decisions while increasingly powerful tools handle more of the execution.
