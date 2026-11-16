# Agentic engineering

The fundamental challenge of agentic software engineering is no longer generating code. It is **maintaining software quality while dramatically increasing the amount of code being produced.**

AI agents can generate, modify, test, and submit code at rates that would have been impossible for human engineering teams. However, increasing code production without improving the engineering environment introduces a serious problem:

**An agent that produces poor code slowly becomes an automated system that produces poor code at scale.**

The solution is to build an engineering environment in which correct implementations are easy to produce, incorrect implementations are difficult to introduce, and the results can be independently verified.

This changes the role of software engineering from primarily writing implementations to designing the constraints, abstractions, and verification mechanisms that make implementations trustworthy.

## 1. Agentic engineering is fundamentally a trust problem

Traditional software development generally involves a human engineer writing code, reviewing changes, running tests, and deploying the result.

Agentic development introduces a potentially large number of autonomous contributors.

```text
Traditional Development
-----------------------

Engineer
   |
   v
Write Code
   |
   v
Review Code
   |
   v
Run Tests
   |
   v
Deploy


Agentic Development
-------------------

   Engineering Environment
            |
  +---------+---------+
  |         |         |
Agent 1   Agent 2   Agent N
  |         |         |
  v         v         v
Code      Code      Code
  |         |         |
  +---------+---------+
            |
            v
   Automated Verification
            |
            v
         Deploy
```

The important difference is that a human cannot reasonably inspect every implementation when hundreds or thousands of changes arrive continuously.

Consequently, the engineering environment must take responsibility for much of the work that previously happened during code review.

This leads to a critical distinction:

- **Blind trust:** Assuming an agent's implementation is correct because the agent claims it is.
- **Engineered trust:** Establishing mechanisms that make the implementation conform to known architectural constraints and demonstrate the required behavior.

**Engineered trust is supported by reproducible evidence, not confidence in the model.**

## 2. The hierarchy of engineering constraints

Not all mechanisms for controlling agent behavior are equally reliable.

A useful hierarchy prioritizes deterministic constraints over instructions written in natural language.

```text
AGENT ENGINEERING ENVIRONMENT
=============================

+--------------------------------+
|   Architecture & API Design    |
|                                |
|  Make invalid designs harder   |
|    or impossible to express    |
+--------------------------------+
                |
                v
+--------------------------------+
|   Deterministic Enforcement    |
|                                |
|   Types, linters, compilers,   |
|     static analysis, tests     |
+--------------------------------+
                |
                v
+--------------------------------+
|          Verification          |
|                                |
|    Runtime, model checking,    |
|     property-based testing     |
+--------------------------------+
                |
                v
+--------------------------------+
|        Natural Language        |
|                                |
|  Rules, skills, instructions,  |
|         documentation          |
+--------------------------------+
```

The first two layers are especially important because their constraints can be enforced mechanically.

Consider a rule:

> Never import database access code directly from the UI layer.

There are several ways to communicate this requirement.

**Approach A: Natural language**

Put the requirement in an `AGENTS.md` file.

This helps an agent understand the intended architecture, but compliance depends on the agent following the instruction.

An agent might ignore it, misunderstand it, or produce an exception.

**Approach B: Static enforcement**

Introduce a dependency rule that rejects prohibited imports.

```text
UI Layer
   |
   v
Application Layer
   |
   v
Persistence Layer


Allowed:

UI ------------> Application
Application ---> Persistence


Forbidden:

UI ------------> Persistence
```

Now, regardless of what the agent decides, the build or validation pipeline can reject a forbidden dependency.

**The architectural constraint no longer depends on the agent remembering the instructions.**

**The general principle is to convert behavioral expectations into executable constraints whenever possible.**

Natural-language instructions remain valuable for communicating goals and judgment, but they should not be the only defense against predictable mistakes.

## 3. The codebase is part of the agent's environment

AI coding agents learn about a repository by reading existing implementations, APIs, tests, comments, and surrounding patterns.

That makes the codebase more than an output artifact. It is also a major source of context for future code generation.

This creates a feedback loop.

```text
Existing Codebase <-----------------+
       |                            |
       v                            |
Agent Reads Existing Patterns       |
       |                            |
       v                            |
Agent Generates Similar Code        |
       |                            |
       v                            |
New Code Enters Repository          |
       |                            |
       v                            |
Future Agents Read New Code         |
       |                            |
       +---------- Repeat ----------+
```

If the repository contains good abstractions and well-enforced boundaries, agents are likely to encounter and reuse those patterns.

If the repository contains workarounds, deprecated APIs, or architectural violations, those patterns can also be reproduced.

### How technical debt becomes self-reinforcing

Imagine a desktop application with a synchronization problem.

An engineer introduces a timer as a temporary workaround:

```javascript
setTimeout(() => { refreshUI(); }, 100);
```

The workaround resolves a visible symptom, but it does not fix the underlying synchronization issue.

Later, another agent encounters a similar problem.

The agent searches the repository and discovers several implementations using timers.

It concludes that timers are the project's established solution.

```text
Architecture Problem
        |
        v
Temporary Timer Workaround <--------+
        |                           |
        v                           |
Agent Observes Existing Pattern     |
        |                           |
        v                           |
Agent Repeats Workaround            |
        |                           |
        v                           |
More Timers and Complexity          |
        |                           |
        v                           |
More Performance Problems           |
        |                           |
        +---- More Workarounds -----+
```

Eventually, the repository accumulates many independent timers, potentially creating unnecessary work, lifecycle complexity, and garbage-collection pressure.

The original problem has become systemic.

This suggests a different approach to technical debt.

**Cleaning up an anti-pattern does more than improve existing code: it removes an undesirable example that future agents might otherwise imitate.**

The economic value of good architecture increases as automated code generation accelerates.

## 4. Eliminate classes of bugs instead of correcting individual mistakes

Traditional code reviews often identify mistakes one at a time.

An agentic engineering environment should turn recurring corrections into permanent improvements.

For example, suppose agents repeatedly misuse a React lifecycle mechanism.

There are two possible solutions.

**Solution A: Repeated correction**

Every time an agent incorrectly uses the mechanism, provide feedback explaining how to fix it.

The cost recurs with every implementation.

**Solution B: Architectural elimination**

Create an abstraction that handles the relevant lifecycle behavior correctly, then restrict direct access to the problematic mechanism in application code.

```text
Before
------

Agent
  |
  v
Low-Level API
  |
  +--> Correct Usage
  |
  +--> Incorrect Usage
  |
  +--> Subtle Lifecycle Bug


After
-----

Agent
  |
  v
Constrained High-Level API
  |
  v
Validated Implementation
  |
  v
Correct Lifecycle Behavior
```

The second solution reduces the number of decisions that every future agent must make.

**An abstraction is particularly valuable when it encodes domain knowledge that would otherwise require careful judgment on every use.**

For example, a desktop application can restrict direct use of `useEffect` in product code while allowing controlled use inside framework abstractions.

Restricting `useEffect` is an application-specific design choice.

**When an API is easy to misuse, replace repeated guidance with an abstraction that makes the intended usage straightforward and enforceable.**

## 5. Prefer fixing the root cause over explaining the workaround

Agents can produce convincing explanations for questionable implementations.

A problematic pattern is adding a comment to justify a workaround instead of addressing the underlying problem.

For example:

```javascript
// Necessary to avoid a rendering race.
// Do not remove this delay.
setTimeout(updateState, 150);
```

The comment might describe the immediate symptom accurately.

But it can also cause future agents to treat an accidental workaround as an architectural requirement.

This is particularly dangerous when comments become stale or provide incorrect explanations.

A more reliable approach is to detect prohibited constructs and produce actionable diagnostics.

```text
Agent Introduces Workaround
            |
            v
       Linter Runs
            |
            v
    Forbidden Pattern?
            |
   +--------+--------+
   |                 |
   No               Yes
   |                 |
   v                 v
Continue       Reject Change
                     |
                     v
              Explain Violation
                     |
                     v
               Fix Root Cause
```

Instead of merely saying that an implementation is forbidden, a good diagnostic explains which abstraction or mechanism should be used.

The important distinction is not between comments and no comments. It is between **unenforceable explanations and enforceable engineering invariants**.

Documentation can still be essential for design rationale, contracts, and operational knowledge.

But documentation should not substitute for programmatically enforced rules where enforcement is feasible.

## 6. Verification becomes the central activity of agentic engineering

When agents generate implementations rapidly, the relative importance of verification increases.

Writing code is no longer necessarily the most expensive part of development.

**Determining whether code is correct becomes a major engineering bottleneck.**

The solution is to invest in multiple forms of verification because different approaches detect different classes of defects.

### Static verification

Static verification checks properties without needing to exercise the complete running application.

Examples include:

- Type checking.
- Dependency boundary enforcement.
- Lint rules.
- Compiler diagnostics.
- Static analysis.

These mechanisms are inexpensive to repeat and particularly effective at rejecting known categories of invalid implementations.

### Runtime verification

Runtime verification gives agents the ability to execute and inspect the software.

For a desktop or web application, that might include browser automation, screenshots, interaction traces, and debugging tools.

```text
Agent Implements Feature
          |
          v
Build Application <---------------------+
          |                             |
          v                             |
Launch Application                      |
          |                             |
          v                             |
Perform User Actions                    |
          |                             |
          v                             |
Observe Actual Behavior                 |
          |                             |
          v                             |
Compare with Expected Behavior          |
          |                             |
       +--+--+                          |
       |     |                          |
     Pass   Fail                        |
       |     |                          |
       v     v                          |
   Evidence  Diagnose                   |
       |     |                          |
       v     +------ Fix and Retry -----+
   Candidate
   for Merge
```

For example, an agent implementing a notification feature should be able to launch the application, trigger a notification, interact with it, and observe whether the expected state transitions occur.

Without runtime verification, the agent might rely entirely on reasoning about source code.

That is often insufficient for discovering integration problems, UI regressions, timing issues, or incorrect assumptions about external components.

### Feature maps

A **feature map** describes the application from the perspective of its users.

For example:

```text
Application
 |
 +-- Conversations
 |     +-- Create Conversation
 |     +-- Open Conversation
 |     +-- Delete Conversation
 |
 +-- Notifications
 |     +-- Receive Notification
 |     +-- Open Notification
 |     +-- Dismiss Notification
 |
 +-- Settings
       +-- Change Theme
       +-- Configure Notifications
```

This provides a shared vocabulary between engineering requirements and agent operations.

Instead of interpreting an ambiguous instruction such as "fix the thing in the sidebar," an agent can associate the request with a known feature and its relevant interactions.

Custom CLI tools can then expose repeatable operations for testing these features, avoiding the need for every agent to rediscover how to interact with the application.

## 7. Formal verification can make behavioral expectations precise

Some bugs are difficult to detect through conventional testing because they involve complex interactions between states, events, or concurrent components.

Consider notifications synchronized across multiple devices.

A user receives a notification on two devices and dismisses it on one.

What should happen if the second device is offline?

What happens if two devices dismiss the notification concurrently?

What happens if synchronization messages arrive out of order?

These are state-machine problems.

```text
Notification State
------------------

     +---------+
     | Created |
     +---------+
          |
          v
     +---------+
     | Visible |
     +---------+
       |     |
   +---+     +------+
   |                |
   v                v
+------+      +-----------+
| Read |      | Dismissed |
+------+      +-----------+
```

The diagram captures only a simple local lifecycle. A multi-device specification must also define the distributed state, synchronization events, and permitted transitions.

Formal methods help make these expectations explicit.

### TLA+ and model checking

TLA+ can describe a system in terms of states, actions, and invariants.

A model checker explores possible executions within a defined model to determine whether specified properties can be violated.

For example:

- **A dismissed notification must not become visible again because an older update arrives.**
- **A notification must not be processed twice when the system requires exactly-once logical handling.**
- **Concurrent updates must respect the defined conflict-resolution rules.**

A model checker can discover sequences of events that violate those properties.

This is especially valuable for concurrency, distributed state, and reconfiguration problems.

### Lean and proofs

Lean provides a different kind of verification: mathematical proofs about formalized definitions and algorithms.

For example, a virtualization algorithm could be checked against properties concerning valid index ranges, ordering, or preservation of layout-related invariants.

However, proving properties of a model does not automatically prove that a rendered UI will never flicker or jitter. The formal specification must accurately capture the behavior that matters, and the implementation must correspond to that specification.

**Formal verification establishes properties of an explicit model or formalization, not unrestricted correctness of the entire application.**

### Property-based testing

Property-based testing provides another complementary mechanism.

Rather than testing only a few hand-written examples, a framework generates many inputs or action sequences and checks general properties.

For a UI component, useful properties could include:

- No visible item has an invalid index.
- Selection always refers to an existing item.
- Scrolling never produces an out-of-bounds access.
- Removing an item preserves the defined ordering of remaining items.

**These mechanisms are complementary rather than interchangeable.**

Static checks enforce structural rules; runtime tests observe actual application behavior; property-based tests explore many cases; formal methods reason about specified behavior over a model.

## 8. Verification artifacts become reviewable evidence

Traditional code review focuses heavily on implementation details.

Agentic workflows can shift part of that effort toward reviewing evidence about observable behavior.

```text
Implementation
      |
      v
Verification Process
      |
      +-- Test Results
      |
      +-- Screenshots
      |
      +-- Recorded Interactions
      |
      +-- State Transitions
      |
      +-- Model-Checking Results
      |
      v
Reviewable Evidence
      |
      v
Merge Decision
```

Suppose an agent implements a new settings panel.

A reviewer may want to understand whether the panel behaves correctly, not just inspect hundreds of lines of UI code.

An interaction recording can demonstrate that relevant controls work. Tests can establish specific behavioral properties. A state-machine specification can clarify intended transitions.

These artifacts reduce the amount of manual investigation required.

**However, evidence must be interpreted within its scope.**

A successful video demonstrates the tested interaction, not every possible interaction. Passing tests establish only the assertions and cases they cover.

The strongest engineering process combines observable evidence with structural guarantees and targeted human review when changes are risky.

## 9. Agent autonomy should be built from the inside out

There are two distinct automation loops.

The **inner loop** is the process of producing a single trustworthy implementation.

```text
INNER LOOP
----------

  Requirement
       |
       v
 Generate Code <----------------+
       |                        |
       v                        |
 Static Checks                  |
       |                        |
       v                        |
 Runtime Tests                  |
       |                        |
       v                        |
 Verify Behavior                |
       |                        |
  +----+----+                   |
  |         |                   |
 Fail      Pass                 |
  |         |                   |
  v         v                   |
Repair   Validated PR           |
  |                             |
  +----------- Repeat ----------+
```

The **outer loop** coordinates agents, tasks, and delivery.

```text
OUTER LOOP
----------

   Event / New Requirement
             |
             v
        Create Tasks
             |
             v
       Launch Agents
             |
   +---------+---------+
   |         |         |
   v         v         v
Task A     Task B     Task C
   |         |         |
   +---------+---------+
             |
             v
   Verified Pull Requests
             |
             v
    Merge / Release Gates
             |
             v
       Production
```

The ordering is important.

Automating the outer loop before establishing a reliable inner loop merely scales existing defects.

A poorly constrained agent might generate a questionable implementation. A hundred poorly constrained agents can produce a hundred questionable implementations simultaneously.

Adding more agents does not solve an unreliable coding process.

**The correct sequence is to establish a reliable inner loop and then increase orchestration and concurrency.**

## 10. Continuous verification can become part of the release process

Once an application has reliable automation interfaces, a release can trigger a new generation of validation work.

For example:

```text
   New Release
        |
        v
Automated Test Agent
        |
        v
Explore Application
        |
        v
  Discover Defect
        |
        v
Reproduce and Diagnose
        |
        v
   Generate Fix <----------------+
        |                        |
        v                        |
 Run Verification                |
        |                        |
   +----+----+                   |
   |         |                   |
  Fail      Pass                 |
   |         |                   |
   v         v                   |
 Retry    Open Fix PR            |
   |         |                   |
   |         v                   |
   |   Merge Policy              |
   |                             |
   +-----------------------------+
```

This can be extended to automated fuzzing, regression exploration, and remediation.

An agent could repeatedly interact with application features, search for unexpected behavior, and propose fixes.

The important architectural feature is the reusable verification infrastructure.

The same application driver, debugging commands, feature map, and validation rules can serve both development agents and post-release testing agents.

Nevertheless, automated merging should remain conditional on the risk of a change, the strength of its tests, and the consequences of failure.

**A passing validation pipeline is not an unconditional guarantee of correctness.**

## 11. The economics of software engineering change

Traditional engineering requires deciding whether the benefit of a test or verification technique justifies its implementation and maintenance cost.

Formal specifications, exhaustive regression suites, and complex test environments can be expensive to create.

Agents can lower the cost of producing and maintaining some of these artifacts.

That changes the economics of verification.

Consider a simplified model:

```text
C_change = C_implementation + C_verification + C_review + C_failure
```

Here, `C_failure` represents the expected cost of defects and their consequences.

Agentic development may dramatically reduce implementation cost while increasing the volume of changes.

Without effective verification, the resulting failure costs can grow substantially.

Investment in static checks, automated tests, and constrained architectures has a fixed upfront cost, but those mechanisms can be reused across many future changes.

Consequently, their cost can be amortized over a much larger number of implementations.

This is why agentic engineering makes previously expensive verification techniques more attractive.

The objective is not necessarily to maximize the number of tests, but to achieve **stronger guarantees and better defect detection at a sustainable cost**.

## 12. Engineering productivity should not be measured by code volume alone

Shipping thousands of pull requests per month, releasing frequently, maintaining a low relative revert rate, and improving application responsiveness are meaningful operational signals.

However, pull-request counts alone do not establish engineering productivity or quality.

A more comprehensive assessment requires several dimensions.

| Dimension       | What matters                                                     |
| --------------- | ---------------------------------------------------------------- |
| Throughput      | How many valuable changes reach production                       |
| Correctness     | How many defects escape verification                             |
| Reliability     | Whether releases preserve availability and expected behavior     |
| Performance     | Whether latency, resource use, and responsiveness improve        |
| Maintainability | Whether architecture and complexity remain manageable            |
| Efficiency      | How much computation and engineering effort each change requires |

A low revert rate is encouraging but does not capture defects that remain undiscovered, changes that are fixed without reverting, or architectural degradation.

Likewise, thousands of small PRs are not necessarily more valuable than hundreds of substantial improvements.

The engineering target is **increasing the delivery rate of useful, correct changes while controlling operational and maintenance costs**.

## 13. The deeper architectural principle: reduce the space of possible mistakes

Every implementation involves decisions.

An unconstrained environment exposes many choices, some of which are subtly incorrect.

A well-designed environment reduces the number of choices that must be made correctly by an individual agent.

```text
Unconstrained Environment
-------------------------

Requirement
    |
    +--> Good Implementation
    |
    +--> Incorrect Abstraction
    |
    +--> Forbidden Dependency
    |
    +--> Workaround
    |
    +--> Hidden Race Condition
    |
    +--> Unnecessary Complexity


Constrained Environment
-----------------------

Requirement
    |
    v
Well-Designed API
    |
    v
Enforced Architecture
    |
    v
Automated Verification
    |
    v
Validated Implementation
```

There are three important mechanisms at work.

**First, architecture reduces ambiguity.** Good abstractions encode decisions about how software should be structured.

**Second, deterministic constraints reject known mistakes.** Types, dependency rules, and static checks prevent specific categories of invalid code from passing through the development process.

**Third, verification detects failures that structural constraints cannot eliminate.** Runtime testing, property-based testing, and formal reasoning provide additional confidence about behavior.

The combination increases the probability that a generated implementation will satisfy the system's requirements.

It also reduces the amount of judgment needed during routine review, freeing engineering attention for complex architectural decisions and unusual failure modes.

## 14. A practical engineering feedback loop

The most consequential practice is to treat agent failures as signals about weaknesses in the engineering environment.

Suppose an agent introduces an unnecessary timer to resolve a race condition.

A purely corrective workflow fixes that particular implementation.

A systematic workflow asks whether the same mistake can be prevented throughout the repository.

```text
    Agent Makes Mistake
             |
             v
   Identify Failure Pattern
             |
             v
   Investigate Root Cause
             |
             v
Can Architecture Prevent It?
             |
      +------+------+
      |             |
     Yes            No
      |             |
      v             v
 Improve API   Add Deterministic Check
      |             |
      +------+------+
             |
             v
Add Regression Verification
             |
             v
Clean Up Existing Violations
             |
             v
Stronger Agent Environment
             |
             v
Future Agents Encounter
Fewer Failure Opportunities
```

For an engineering organization, this establishes a compounding improvement process.

Each discovered failure becomes an opportunity to strengthen the environment.

Each additional constraint reduces repeated review work.

Each reliable verification mechanism increases the range of changes that can be handled autonomously.

**The resulting autonomy is a consequence of engineering improvements, not merely increasingly capable models.**

## Final engineering lessons

1. **Invest in the environment before scaling the agents.** An agent's effectiveness is constrained by the quality of the codebase, APIs, tooling, and tests it operates within.
2. **Turn recurring corrections into deterministic enforcement.** If the same mistake is repeatedly observed, encode the requirement in types, architecture, or automated checks rather than relying only on prompts.
3. **Eliminate entire categories of mistakes.** A well-designed abstraction is often more valuable than repeatedly detecting misuse of a lower-level API.
4. **Treat verification as a core development capability.** Agents need to execute software, observe its behavior, inspect failures, and produce evidence that implementations satisfy requirements.
5. **Scale orchestration only after the inner development loop is reliable.** More autonomous agents multiply the characteristics of the underlying engineering process, including its weaknesses.

**Agentic engineering is as much about designing systems for agents to work within as it is about designing the agents themselves.**

The greatest productivity gains emerge when architecture, automated enforcement, and verification make correct software the natural outcome of the development process, rather than an exception achieved through repeated human intervention.
