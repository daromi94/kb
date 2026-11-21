# Agentic engineering

The fundamental shift in agentic engineering is moving from **using AI agents to write code** toward **designing engineering environments in which agents can reliably produce, verify, and deliver software with minimal human intervention**.

The primary bottleneck is no longer necessarily code generation. It is the infrastructure surrounding code generation: verification, context delivery, coordination, constraints, and the ability to make correct decisions independently.

This changes the nature of software engineering.

Instead of optimizing how quickly an individual agent completes a task, the engineering problem becomes:

**How can an entire system of agents continuously produce correct changes without requiring a human to supervise every step?**

## 1. The environment matters more than the prompt

A common approach to agentic coding is to improve prompts whenever an agent makes a mistake.

An agent creates a poorly structured component, so additional instructions are added:

- Avoid large files.
- Follow existing patterns.
- Prefer reusable abstractions.
- Keep features isolated.
- Use consistent naming conventions.

This can improve behavior, but it has a fundamental limitation: **the agent must remember, interpret, and correctly apply those instructions every time.**

**A more reliable approach is to encode those requirements directly into the engineering environment.**

For example, instead of instructing an agent not to create enormous files, enforce architectural boundaries through project conventions and lint rules.

Instead of requesting that every feature follow a particular structure, provide a framework where features have a single conventional location.

```text
                   Agent
                     |
                     v
             Generate a change
                     |
                     v
          Engineering environment
                     |
   +-----------------+-----------------+
   |                 |                 |
   v                 v                 v
 Types             Lint          Architecture
checks             rules          constraints
   |                 |                 |
   +-----------------+-----------------+
                     |
                     v
               Valid change
```

The key engineering principle is **make the correct behavior the easiest behavior**.

This resembles the purpose of type systems.

A broad type permits many possible states. A narrow type restricts the system to a smaller set of valid states.

The same reasoning applies to software architecture:

```text
Unconstrained codebase
    |
    +-- Many possible file locations
    +-- Many implementation patterns
    +-- Many dependency structures
    +-- Many ways to represent state
    |
    v
Large space of possible implementations


Constrained codebase
    |
    +-- Conventional feature directories
    +-- Enforced dependency boundaries
    +-- Standardized APIs
    +-- Restricted state management
    |
    v
Smaller space of valid implementations
```

**Reducing the number of possible implementations reduces the number of decisions an agent must make.**

That improves consistency and makes behavior easier to verify.

### Engineering lesson

**Agent reliability is partially an architectural property of the codebase.**

A poorly structured codebase forces every agent to rediscover conventions and make architectural decisions independently.

A well-structured codebase encodes those decisions once and makes them reusable across all agents.

This means refactoring, creating architectural constraints, and building developer tooling can have a greater long-term impact than improving individual prompts.

## 2. Verification is the foundation of agent autonomy

An agent capable of writing code is not necessarily capable of completing an engineering task independently.

Consider a performance optimization.

An agent might identify an expensive computation, refactor it, and produce code that looks more efficient.

But several important questions remain:

- Does the application still work?
- Did the optimization actually improve performance?
- Were regressions introduced?
- Is the measured improvement reproducible?
- Does the change behave correctly under realistic workloads?

Without access to execution and measurement tools, the agent cannot answer these questions reliably.

It must depend on a human to run the application, inspect the output, and report problems.

That makes the human part of the execution loop.

### Before autonomous verification

```text
          Agent
            |
            v
  Write implementation
            |
            v
 Human runs application
            |
            v
 Human observes behavior
            |
            v
 Human reports problems
            |
            v
Agent attempts correction
```

The human becomes the bottleneck.

### With autonomous verification

```text
         Agent
           |
           v
    Form hypothesis
           |<--------------------------------------------+
           v                                             |
   Implement change                                      |
           |                                             |
           v                                             |
    Run application                                      |
           |                                             |
           v                                             |
 Execute verification                                    |
           |                                             |
           v                                             |
 Collect measurements                                    |
           |                                             |
           v                                             |
   Evaluate results                                      |
           |                                             |
    +------+------+                                      |
    |             |                                      |
 Failed        Passed                                    |
    |             |                                      |
    v             v                                      |
Diagnose      Complete                                   |
    |                                                    |
    +---------------- Implement change ------------------+
```

The important improvement is not merely the ability to run tests.

It is the ability to **observe the consequences of an implementation and use those observations to determine the next action**.

Verification can involve unit tests, integration tests, browser automation, performance profiles, memory snapshots, execution traces, or interaction with a running application.

The appropriate mechanism depends on the task.

### Verification enables hill climbing

**Hill climbing** is an optimization strategy in which a system repeatedly modifies a candidate solution and measures whether the result improves.

For example, an agent optimizing UI performance could use the following loop:

```text
Baseline:
    Rendering time = 120 ms

Iteration 1:
    Change implementation
    Rendering time = 95 ms
    Accept improvement

Iteration 2:
    Change implementation
    Rendering time = 110 ms
    Reject regression

Iteration 3:
    Change implementation
    Rendering time = 78 ms
    Accept improvement
```

Illustrative measurements.

The necessary components are:

1. **A measurable objective.**
2. **An execution environment.**
3. **A feedback mechanism.**
4. **A way to preserve improvements and reject regressions.**

The agent can then explore alternatives without requiring human judgment after every modification.

However, the objective must represent the actual engineering goal. Optimizing rendering time alone could produce unacceptable memory usage or broken functionality.

**For this reason, hill climbing should be constrained by correctness requirements and other performance budgets.**

### Engineering lesson

**Autonomy is limited by verifiability.**

**An agent should only operate independently to the degree that its results can be reliably checked.**

Greater code-generation capability does not eliminate this requirement.

## 3. Separate deterministic work from agent judgment

Not every engineering operation requires artificial intelligence.

Many tasks are fundamentally mechanical:

- Running tests.
- Formatting code.
- Collecting performance traces.
- Transforming syntax trees.
- Generating repetitive boilerplate.
- Applying standardized migrations.
- Validating architectural constraints.

Allowing agents to reinvent these operations repeatedly introduces unnecessary uncertainty.

For example, consider an agent that needs to inspect browser performance.

Without a reusable tool, it might generate a new browser automation script for every task.

Different agents will produce different scripts, potentially with different assumptions, errors, and measurement procedures.

A better approach is to provide a deterministic CLI that exposes stable operations.

```text
                     Agent
                       |
                       v
            Decide what to inspect
                       |
                       v
               Verification CLI
                       |
   +-------------------+-------------------+
   |                   |                   |
   v                   v                   v
Browser             Traces              Metrics
control             capture           collection
   |                   |                   |
   +-------------------+-------------------+
                       |
                       v
              Structured results
                       |
                       v
                     Agent
              Interpret evidence
```

**The agent determines what needs investigation.**

**The CLI determines how the investigation is executed.**

This creates a useful division of responsibility:

| Responsibility                      | Best mechanism           |
| ----------------------------------- | ------------------------ |
| Understanding a problem             | Agent reasoning          |
| Choosing an investigation           | Agent reasoning          |
| Running a known procedure           | Deterministic tool       |
| Collecting measurements             | Deterministic tool       |
| Interpreting ambiguous results      | Agent reasoning          |
| Enforcing invariants                | Types, tests, lint rules |
| Applying mechanical transformations | Scripts or codemods      |

The result is more consistent, efficient execution.

It also reduces context consumption because agents no longer need to reconstruct implementation details of well-established workflows.

### Engineering lesson

**Use agents for judgment and software for repeatability.**

A recurring deterministic procedure should eventually become a reusable tool rather than remaining an instruction that an agent interprets from scratch.

This is particularly valuable for migrations, verification, performance analysis, and code maintenance.

## 4. Agentic engineering has two interconnected control loops

An autonomous coding agent can operate effectively when given a task with complete context.

But engineering context changes continuously.

Bug reports arrive. Requirements evolve. Production systems exhibit new failures. Other engineers modify shared components.

A coding agent working from an initial prompt does not automatically know about those events.

Its understanding of the desired outcome is effectively a snapshot.

That snapshot becomes stale.

A more scalable architecture separates two responsibilities.

### The inner loop: engineering execution

**The inner loop converts intent into implemented and verified changes.**

Typical responsibilities include planning, implementation, testing, debugging, and preparing pull requests.

### The outer loop: context acquisition and prioritization

**The outer loop observes the surrounding environment and supplies new information to the engineering system.**

Sources can include issue trackers, bug reports, communication channels, repository events, and operational signals.

```text
                   OUTER LOOP
         External information and events
       +--------------------------------+
       | Issue trackers                 |
       | Bug reports                    |
       | Engineering discussions        |
       | Repository observations        |
       | Operational signals            |
       +--------------------------------+
                        |<----------------------------------------+
                        v                                         |
                 Context intake                                   |
                        |                                         |
                        v                                         |
                 Triage / Group                                   |
                        |                                         |
                        v                                         |
                Coordinator agent                                 |
                        |                                         |
    +-------------------+-------------------+                     |
    |                   |                   |                     |
    v                   v                   v                     |
 Agent A             Agent B             Agent C                  |
    |                   |                   |                     |
    v                   v                   v                     |
Implement           Implement           Implement                 |
    |                   |                   |                     |
    v                   v                   v                     |
 Verify              Verify              Verify                   |
    |                   |                   |                     |
    +-------------------+-------------------+                     |
                        |                                         |
                        v                                         |
                  Pull requests                                   |
                        |                                         |
                        v                                         |
                 Merge / Observe                                  |
                        |                                         |
                        v                                         |
                  New feedback                                    |
                        |                                         |
                        +-------------- Outer loop ---------------+
```

The benefit is that humans no longer need to manually transfer every piece of external context into an agent conversation.

But this architecture introduces new distributed-systems problems.

Events can arrive out of order. Reports can be duplicated. Multiple agents may race to fix the same issue. New context may invalidate work already in progress.

A production implementation therefore needs mechanisms for deduplication, task ownership, cancellation, prioritization, and reconciliation.

### Engineering lesson

**An autonomous engineering system must manage changing context, not merely execute a static task list.**

Giving agents access to code is insufficient if critical information remains outside their execution environment.

## 5. Coordination is more valuable than indiscriminate parallelism

Suppose 30 bug reports arrive within a short period.

One possible architecture creates 30 agents, each independently investigating one report.

This looks scalable, but can be inefficient.

Several reports may describe different symptoms of the same underlying problem.

For example:

```text
Bug A: UI freezes when switching tabs --------------------+
                                                          |
Bug B: Memory usage grows over time ----------------------+
                                                          |
Bug C: Navigation becomes progressively slower -----------+
                                                          |
Bug D: Rendering stalls after many updates ---------------+
                                                          |
                              +---------------------------+
                              |
                              v
                  Shared underlying problem
                              |
                              v
                  Excessive retained state
```

Thirty independently spawned agents may repeatedly investigate the same subsystem, implement overlapping fixes, and create conflicting pull requests.

A coordinator can instead analyze the reports collectively.

```text
          Incoming reports
                  |
                  v
             Coordinator
                  |
                  v
           Group by cause
                  |
      +-----------+-----------+
      |                       |
      v                       v
  Problem A               Problem B
      |                       |
      v                       v
Worker agent            Worker agent
      |                       |
      v                       v
  Verified                Verified
     fix                     fix
```

The coordinator's purpose is not simply to delegate work.

**It should maintain a broader understanding of the problem space, avoid redundant execution, and reconcile discoveries across workers.**

This is similar to the distinction between coordinating a distributed computation and blindly distributing every task.

### Not every observation should trigger immediate execution

Some findings are better accumulated in a queue.

Consider an agent continuously inspecting a codebase for suspicious patterns.

Rather than immediately creating a PR for each observation, it can append findings to a shared artifact.

After enough observations accumulate, recurring patterns become visible.

```text
  Continuous inspection
            |
            v
     Findings queue
            |
            v
    Periodic analysis
            |
            v
 Identify common causes
            |
            v
   Choose systemic fix
            |
            v
One architectural change
```

This creates an opportunity to solve a class of problems instead of individual symptoms.

For example, discovering 40 instances of an incorrect state-management pattern might justify a lint rule or framework change rather than 40 independent fixes.

### Engineering lesson

**Optimize for reducing total engineering work, not maximizing the number of active agents.**

Parallelism increases throughput only when the work can be decomposed effectively.

Poor coordination creates duplication, conflicts, and integration overhead.

## 6. Continuous codebase gardening is essential infrastructure

A codebase gradually accumulates complexity.

Even when individual changes are correct, repeated local decisions can introduce:

- Duplicate abstractions.
- Large, difficult-to-maintain files.
- Inconsistent implementation patterns.
- Architectural boundary violations.
- Unnecessary dependencies.
- Performance anti-patterns.

Agentic coding can accelerate this accumulation because agents are optimized to complete immediate tasks, not necessarily to maintain long-term architectural consistency.

A useful solution is continuous codebase gardening.

This means dedicating agent capacity to identifying and reducing structural problems rather than exclusively implementing features.

**The most important part is converting recurring failures into permanent improvements.**

```text
   Observe agent behavior
              |
              v
  Detect recurring mistake
              |
              v
     Analyze root cause
              |
              v
    Can it be prevented?
              |
    +---------+---------+
    |                   |
   Yes                 No
    |                   |
    v                   v
Add guard       Improve workflow
 or tool         or verification
    |                   |
    +---------+---------+
              |
              v
   Run across future tasks
              |
              v
     Measure recurrence
```

For example:

**Observation:** Agents repeatedly append new functionality to a massive central file.

**Root cause:** The architecture does not establish a clear place for independent features.

**Systemic change:** Introduce feature directories, a feature registry, and rules that enforce module boundaries.

**Result:** Future agents operate inside a structure where the undesirable approach is harder or impossible.

One architectural improvement can prevent hundreds of future mistakes.

### Engineering lesson

**Every recurring agent failure is potential feedback about the environment.**

The correct response is often not to fix the current agent but to improve the system in which all future agents operate.

This changes code review from exclusively detecting defects to discovering opportunities for systemic improvements.

## 7. Trust should be earned through evidence

Agent autonomy is not binary.

It develops as the engineering system gains stronger verification mechanisms, more predictable conventions, and better operational safeguards.

A useful progression is:

```text
Level 1: Human-directed execution
         Agent writes code
         Human verifies everything
                    |
                    v
Level 2: Assisted verification
         Agent runs tests and tools
         Human evaluates results
                    |
                    v
Level 3: Autonomous iteration
         Agent implements and verifies
         Human reviews final changes
                    |
                    v
Level 4: Conditional autonomous merge
         Agent verifies and merges
         Human audits selected outcomes
                    |
                    v
Level 5: Continuous autonomous operation
         External signals trigger work
         Agents coordinate and deliver
         Humans improve the system
```

The critical distinction is that each level requires additional evidence of reliability.

A system should not advance simply because an agent occasionally produces excellent code.

**Reliability must be repeatable under realistic conditions.**

This is also why autonomous verification becomes particularly important before allowing agents to merge their own changes.

A mature workflow may involve independent verifier agents, integration tests, application-level interactions, and attempts to discover regressions.

**The goal is to prevent an implementing agent from being the sole judge of its own work.**

### The limits of verification

Some changes are reversible.

A UI styling bug can often be corrected through a subsequent deployment or rollback.

Others are effectively irreversible:

- Deleting production data.
- Triggering financial transactions.
- Introducing security vulnerabilities.
- Corrupting durable state.
- Performing destructive schema migrations.

These operations require stronger controls.

**Automated testing cannot establish correctness beyond the properties and scenarios actually checked.**

**Even formal verification proves properties relative to a specification and its assumptions.** It does not establish that the specification captures every real-world requirement.

**Therefore, autonomy should depend on both verification confidence and the consequences of failure.**

| Change class                          | Appropriate autonomy                                  |
| ------------------------------------- | ----------------------------------------------------- |
| Formatting and mechanical refactoring | High, with automated checks                           |
| Low-risk isolated feature             | Conditional autonomous merge                          |
| Performance optimization              | Require measurable improvements and regression checks |
| Authentication or authorization logic | Stronger independent review                           |
| Destructive data migration            | Human approval and explicit safety procedures         |

### Engineering lesson

**Trust is a property of the entire workflow, not a belief in the model.**

Strong autonomy results from an accumulation of evidence, constraints, and operational controls.

## 8. The real goal is to remove humans from repetitive decisions

Human involvement is expensive when the same decision must be repeated thousands of times.

Consider three situations.

In the first, an agent asks where to put a new feature.

The answer should probably become a project convention.

In the second, an agent asks how to reproduce a particular class of bug.

The procedure should probably become a verification tool.

In the third, an agent asks for context from a bug report.

The system should probably provide access to the relevant source.

These are different manifestations of the same underlying problem:

**Knowledge necessary for execution exists only in a human's head or in an inaccessible system.**

A mature agentic engineering environment gradually externalizes that knowledge.

```text
Human expertise
      |
      +-- Architectural decisions --> Constraints
      |
      +-- Repeated procedures ------> Tools / CLIs
      |
      +-- Engineering judgment -----> Skills
      |
      +-- External information -----> Connectors
      |
      +-- Quality expectations -----> Verification
      |
      v
Reusable engineering infrastructure
      |
      v
Many agents benefit simultaneously
```

This resembles the principle of _context, not control_.

Instead of directing every action, the system provides sufficient context, tools, and constraints for agents to make appropriate decisions independently.

The distinction matters because micromanagement does not scale linearly with increasing numbers of agents.

If each agent requires constant intervention, adding agents simply increases coordination overhead.

**The real productivity improvement appears when agents can resolve routine questions without human assistance.**

## 9. Skills are executable engineering processes expressed as instructions

An agent skill should not be treated as a magical prompt.

It is a reusable description of how a particular class of work should be performed, optionally supported by deterministic tools.

**Good skills capture proven engineering workflows.**

For example, a performance investigation skill might specify:

```text
 Performance investigation
             |
             v
    Reproduce the issue
             |
             v
   Establish a baseline
             |
             v
Collect profiling evidence
             |
             v
  Identify the bottleneck
             |
             v
     Form a hypothesis
             |
             v
Implement a targeted change
             |
             v
       Measure again
             |
             v
   Validate correctness
```

The skill should guide the process rather than prescribe every implementation detail.

As agent capabilities improve, there is less benefit in documenting trivial operations that the agent can infer reliably.

The most valuable content becomes the reasoning structure: what evidence to gather, which decisions matter, and what constitutes completion.

### Mining agent histories for skills

Agent conversations contain a record of actual engineering behavior.

They expose moments when an agent misunderstood requirements, selected the wrong abstraction, omitted verification, or required correction.

These histories can be analyzed to extract reusable processes.

```text
Historical agent conversations
               |
               v
    Identify interventions
               |
               v
    Find recurring patterns
               |
               v
     Extract general rule
               |
     +---------+---------+
     |                   |
     v                   v
 Workflow           Constraint
   skill              or tool
     |                   |
     +---------+---------+
               |
               v
  Apply to future executions
```

This is more informative than constructing skills entirely from hypothetical best practices.

It captures where the real system repeatedly fails.

**An important distinction is that not every correction should become another instruction.**

Sometimes the better solution is a lint rule, a CLI, an architectural refactoring, or an automated test.

### Engineering lesson

**Skills should encode judgment-intensive workflows; deterministic constraints should be enforced outside the agent wherever practical.**

This produces smaller, more understandable skills and more reliable execution.

## 10. Scaling agentic engineering is an exercise in systems engineering

A system producing thousands of pull requests is not necessarily a system implementing thousands of independent features.

Its output may include maintenance, refactoring, mechanical changes, fixes, experiments, and codebase gardening.

**Raw PR volume therefore says little about engineering quality.**

The interesting architectural achievement is not the number of pull requests.

It is the ability to sustain many concurrent engineering activities without proportionally increasing human supervision.

That requires solving familiar systems-engineering problems:

| Problem           | Agentic engineering equivalent                       |
| ----------------- | ---------------------------------------------------- |
| Scheduling        | Assigning work to agents                             |
| Admission control | Limiting concurrent tasks                            |
| Backpressure      | Preventing incoming work from overwhelming execution |
| Deduplication     | Avoiding repeated fixes for the same issue           |
| Isolation         | Preventing agents from interfering with one another  |
| Consistency       | Reconciling overlapping code changes                 |
| Observability     | Measuring agent execution and quality                |
| Fault tolerance   | Recovering from failed or interrupted tasks          |
| Feedback control  | Adjusting workflows based on observed failures       |

These considerations become increasingly important as autonomy increases.

An architecture that works with three agents may behave very differently with hundreds.

For example, creating more agents may increase the number of generated changes while making integration and verification the new bottlenecks.

In that situation, **additional code-generation capacity does not improve the throughput of correct, merged changes.**

The relevant metric is closer to:

**Verified, useful changes delivered per unit of time and cost**, subject to acceptable failure rates.

PR count alone does not capture this.

## 11. The ultimate engineering pattern: optimize the system, not the individual agent

All of these principles converge on a single architecture.

```text
                EXTERNAL ENVIRONMENT
                          |
             Events, bugs, requirements
                          |
                          v
                   CONTEXT INTAKE
                          |
                          v
                TRIAGE AND PRIORITIZE
                          |
                          v
                     COORDINATOR
                          |
                   Plan / Delegate
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       Agent A         Agent B         Agent C
          |               |               |
          +---------------+---------------+
+------------------------>|
|                         v
|               CONSTRAINED CODEBASE
|                         |
|                Types / Lint / APIs
|                         |
|                         v
|                   VERIFICATION
|                         |
|             Tests / Runtime / Metrics
|                         |
|           +-------------+-------------+
|           |                           |
|           v                           v
|         Fail                        Pass
|           |                           |
|           v                           v
|       Iteration                  Risk gates
|           |                           |
+-----------+                           |
                                        v
                                 Merge / Deploy
                                        |
                                        v
                                Observe outcomes
                                        |
                                        v
                                  QUALITY AUDIT
                                        |
                                        v
                             ENVIRONMENT IMPROVEMENT
                                        |
              +-------------------------+-------------------------+
              |                         |                         |
              v                         v                         v
          New skill               New guardrail               New tool
              |                         |                         |
              +-------------------------+-------------------------+
                                        |
                                        v
                             FUTURE AGENT EXECUTIONS
```

This reveals two forms of improvement.

**The execution loop** improves an individual change until it satisfies verification requirements.

**The system improvement loop** examines failures across many executions and changes the environment to prevent those failures from recurring.

The second loop is especially important.

It means the engineering organization can improve not only the software it delivers, but also the process responsible for delivering software.

A recurring failure becomes a new constraint. A repetitive procedure becomes a tool. A missing context source becomes an integration. An unreliable workflow becomes a better skill.

Over time, these improvements compound.

## Final engineering principles

1. **Optimize the environment before scaling agents.** Architecture, tooling, and constraints determine how reliably agents operate.
2. **Verification is the prerequisite for autonomy.** Agents need independent access to execution, observation, and measurement.
3. **Make correctness the path of least resistance.** Encode recurring decisions in types, conventions, tools, and architectural rules.
4. **Separate reasoning from mechanical execution.** Preserve agent judgment for problems that genuinely require it.
5. **Connect external context to execution.** Autonomous engineering needs continuous access to changing requirements and operational evidence.
6. **Coordinate before parallelizing.** More agents are not necessarily more productive agents.
7. **Convert repeated mistakes into systemic improvements.** Preventing a failure is more valuable than correcting it indefinitely.
8. **Match autonomy to verifiability and risk.** Irreversible changes demand stronger guarantees and controls.
9. **Measure outcomes rather than activity.** PR count and agent count are poor substitutes for quality, throughput, and reliability.
10. **Treat the agentic engineering environment as a product.** Its architecture, correctness, observability, and maintainability deserve the same rigor as production software.

The deepest shift is that **engineering expertise becomes increasingly valuable when encoded into reusable systems rather than applied manually to individual changes**.

The highest-leverage engineering work is no longer necessarily implementing the next feature. It may be creating the constraint, verification mechanism, or workflow that allows hundreds of future features to be implemented correctly without repeated human intervention.
