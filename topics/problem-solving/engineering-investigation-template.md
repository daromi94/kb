# Engineering Investigation Template

The Engineering Investigation Template is a structured way to investigate problems, reason about their causes, evaluate possible solutions, and make defensible technical decisions.

Its purpose is to prevent one of the most common mistakes in software engineering:

Jumping from a symptom directly to a solution without understanding the problem.

For example:

> A distributed query engine is experiencing high latency. Let's increase the number of workers.

That might solve the problem. But what if the real bottleneck is the coordinator? What if increasing workers creates more network contention? What if the actual problem is unbounded concurrency?

Engineering investigation provides a disciplined way to answer these questions.

## 1. The overall mental model

```text
     OBSERVATION
          |
          v
+--------------------+
| 1. Problem         |
+--------------------+
          |
          v
+--------------------+
| 2. Constraints     |
+--------------------+
          |
          v
+--------------------+
| 3. Hypotheses      |
+--------------------+
          |
          v
+--------------------+
| 4. Evidence        |
+--------------------+
          |
          v
+--------------------+
| 5. Experiment      |
+--------------------+
          |
          | If inconclusive:
          +----> New hypotheses
          |
          v
+--------------------+
| 6. Alternatives    |
+--------------------+
          |
          v
+--------------------+
| 7. Decision        |
+--------------------+
          |
          v
+--------------------+
| 8. Validation      |
+--------------------+
          |
          v
+--------------------+
| 9. Failure modes   |
+--------------------+
```

These steps are not necessarily linear. Evidence can invalidate hypotheses, experiments can reveal new constraints, and validation can uncover unexpected failures.

The essential distinction is between understanding the problem and choosing how to solve it.

Let's go through every section using one hypothetical example.

## 2. Problem — What is happening, and why does it matter?

The first step is to describe the observed behavior without making assumptions about its cause.

Imagine a distributed query engine with 10 workers.

Under normal load, the engine performs well. But as concurrency increases, performance deteriorates.

Poor problem statement:

> The query engine needs admission control.

This already assumes a solution.

Better problem statement:

> When concurrent queries exceed approximately 100, p99 latency increases from 400 ms to 5 seconds. Throughput stops increasing, and some workers occasionally crash.

The second statement is useful because it identifies measurable symptoms.

A well-framed problem should establish:

- Expected behavior: What should the system do?
- Actual behavior: What is happening instead?
- Impact: Why does it matter?
- Conditions: Under what workload or circumstances does it occur?

The goal is not to explain why the problem exists yet.

Engineering principle: Separate observations from interpretations.

## 3. Constraints — What must remain true?

Before proposing a solution, it's necessary to understand the boundaries within which the system operates.

Engineering is fundamentally about making decisions under constraints.

For example, suppose the query engine has these requirements:

| Constraint   | Requirement                                             |
| ------------ | ------------------------------------------------------- |
| Latency      | p99 below 1 second for completed interactive queries    |
| Availability | At least 99.9% successful requests under supported load |
| Resources    | Maximum of 10 worker nodes                              |
| Workload     | Queries have highly variable memory requirements        |
| Cost         | Infrastructure spending cannot increase                 |

These are hypothetical requirements, not conclusions about the system.

Why do they matter?

Consider three proposed solutions:

**Solution A:** Increase the number of workers. It might help, but violates the resource and cost constraints.

**Solution B:** Introduce an unbounded queue. It might prevent immediate rejection, but could violate the latency requirement and create memory pressure.

**Solution C:** Implement bounded admission control. It might stabilize resource consumption, but rejecting excess queries could violate the availability requirement, depending on how availability is defined.

None of these solutions can be evaluated properly without first understanding the constraints.

Also, constraints should be challenged when necessary. A 99.9% success target might be unrealistic at arbitrarily high offered load; the supported workload and overload behavior must be defined.

Engineering principle: A solution isn't good in isolation. It's good relative to specific requirements and constraints.

## 4. Hypotheses — What could explain the behavior?

This is one of the most important sections.

A hypothesis is a testable explanation of an observation.

For example, there are several possible causes of the query engine's latency problem.

### Hypothesis A — CPU saturation

Workers are receiving more computational work than their available CPU capacity can process.

**Prediction:** CPU utilization or throttling should increase as throughput plateaus, and runnable work may accumulate.

### Hypothesis B — Memory pressure

Too many concurrently executing queries consume excessive memory, triggering garbage collection, spilling, or worker crashes.

**Prediction:** Peak memory usage and memory-related stalls or failures should correlate with higher concurrency.

### Hypothesis C — Coordinator bottleneck

The coordinator cannot schedule work as fast as requests arrive.

**Prediction:** Scheduling delay or coordinator queue depth should grow even when workers have spare capacity.

### Hypothesis D — Network contention

Data exchange between workers is becoming a bottleneck.

**Prediction:** Network throughput, retransmissions, or exchange wait times should indicate increasing network-related delays.

Notice that each hypothesis has a corresponding prediction.

This is crucial.

A weak hypothesis is merely a guess:

> Perhaps the problem is memory.

A stronger hypothesis is testable:

> Increasing concurrent query execution causes worker memory usage to approach its limit, producing memory stalls and eventually crashes.

Now there is something concrete to investigate.

It's also possible for multiple hypotheses to be true simultaneously.

Engineering principle: A useful hypothesis explains the observations and predicts evidence that could disprove it.

## 5. Evidence — What do we know, and what is missing?

The purpose of collecting evidence is to determine which hypotheses remain plausible.

Suppose monitoring provides the following measurements:

| Metric                      | Observation                   |
| --------------------------- | ----------------------------- |
| Worker CPU                  | 45% average                   |
| Worker memory               | 95% on some workers           |
| Coordinator CPU             | 30%                           |
| Network utilization         | 20% of measured link capacity |
| Query execution concurrency | Grows with incoming requests  |
| Worker crashes              | OOM events during peak load   |

This evidence makes memory pressure a strong candidate.

However, there are important nuances.

- Average CPU utilization can hide saturation on individual cores.
- Low average network utilization doesn't eliminate network hotspots.
- High memory usage doesn't independently prove memory is causing latency.
- OOM events demonstrate a memory failure, but not necessarily why memory grew.

A strong investigation asks whether measurements are sufficiently granular and whether they cover the relevant time window.

For distributed systems, averages across nodes are often particularly misleading.

```text
Worker A:  Memory  45%
Worker B:  Memory  50%
Worker C:  Memory  96%  <-- Possible hotspot
Worker D:  Memory  42%
Worker E:  Memory  48%
```

Cluster-wide averages can obscure the node responsible for failures.

Engineering principle: Measurements should distinguish competing explanations, not merely describe system activity.

## 6. Experiment — What test can distinguish the hypotheses?

Evidence collected from production is often observational. Experiments provide a stronger way to establish causality.

Suppose the leading hypothesis is that excessive concurrent query execution causes memory exhaustion.

A useful experiment is to control the number of executing queries while keeping the workload and worker resources fixed.

| Max executing queries | Throughput   | p99 latency | Peak memory |
| --------------------- | ------------ | ----------- | ----------- |
| 10                    | 30 queries/s | 250 ms      | 40%         |
| 25                    | 65 queries/s | 400 ms      | 65%         |
| 50                    | 75 queries/s | 1.2 s       | 85%         |
| 100                   | 73 queries/s | 5.0 s       | 98%         |

Illustrative experimental results, not measurements from a real system.

What could these results suggest?

First, increasing concurrency initially improves throughput.

Second, after a certain point, increasing concurrency produces diminishing returns and eventually worse latency.

Third, memory usage continues increasing even when throughput stops improving.

This is consistent with a system operating beyond an efficient concurrency level.

But there is an important distinction: correlation between concurrency and memory growth doesn't prove that memory is the only cause of the latency increase. Additional experiments could investigate garbage collection, spilling, and query-level memory usage.

Another subtle point is that limiting execution concurrency may move waiting time into a coordinator queue. Total end-to-end latency must also be measured.

A good experiment should define the workload, variables, predicted outcomes, metrics, and conditions under which the hypothesis would be rejected.

Engineering principle: Experiments are not just for verifying solutions. They are for improving understanding of how the system behaves.

## 7. Alternatives — What solutions are available, and what are their trade-offs?

Once the problem is sufficiently understood, compare competing approaches.

For the memory-pressure example, potential solutions include:

| Alternative                    | Advantages                               | Disadvantages                                     |
| ------------------------------ | ---------------------------------------- | ------------------------------------------------- |
| Limit concurrent queries       | Bounds the amount of admitted work       | Can introduce waiting or rejection                |
| Bounded execution queue        | Absorbs short bursts                     | Increases waiting latency                         |
| Memory-aware admission control | Accounts for variable query requirements | Requires estimates and more complex scheduling    |
| Optimize query memory usage    | Improves resource efficiency             | May require substantial engineering work          |
| Add workers                    | Distributes resource consumption         | Additional cost and potentially more coordination |

An experienced engineer doesn't simply ask which alternative is fastest to implement.

The evaluation should consider:

- Performance and scalability
- Reliability and failure behavior
- Implementation and operational complexity
- Cost and resource efficiency
- Reversibility and future maintenance

For example, bounded admission control may be attractive as an immediate mitigation while query memory optimization is investigated as a longer-term solution.

The trade-off is that overload must now be handled explicitly through queueing, rejection, or some other policy.

Engineering principle: Engineering decisions rarely involve a universally best solution. They involve selecting an appropriate trade-off.

## 8. Decision — What should be done, and why?

A technical decision should record both the selected approach and the reasoning behind it.

For example:

> Decision: Introduce bounded query execution concurrency, with a limited waiting queue and explicit overload rejection.
>
> Rationale: Experiments indicate that increasing execution concurrency beyond a certain level does not improve throughput but substantially increases memory usage and tail latency.
>
> Rejected alternative: Increasing worker count would raise infrastructure costs and might mask inefficient resource management.
>
> Uncertainty: Memory-aware admission control may ultimately be more effective because query memory requirements vary.
>
> Revisit when: Workload characteristics change significantly or the concurrency limit consistently underutilizes worker capacity.

Notice that the decision isn't presented as an absolute truth.

It documents the evidence, assumptions, alternatives, and remaining uncertainty.

This is closely related to an Architecture Decision Record (ADR).

One of the most valuable engineering habits is documenting why a decision was made. That makes future changes much easier to reason about.

## 9. Validation — How will we know the decision worked?

Implementing a change doesn't mean solving the problem.

Validation compares actual outcomes against success criteria defined in advance.

For example, after introducing bounded concurrency:

| Metric                           | Before          | Target after                     |
| -------------------------------- | --------------- | -------------------------------- |
| p99 latency for admitted queries | 5 seconds       | Under 1 second                   |
| Worker OOM crashes               | Occasional      | Zero during the test             |
| Completed throughput             | 73 queries/s    | At least 73 queries/s            |
| Queue waiting time               | Unmeasured      | Bounded and observable           |
| Rejected requests                | None explicitly | Within an agreed overload policy |

The targets are hypothetical.

Here is the subtlety: an admission-control mechanism can make latency for admitted queries look much better by rejecting a large portion of the incoming traffic.

That doesn't necessarily mean the overall user experience improved.

Validation must consider rejected requests, retries, total offered load, and end-to-end latency, not just the latency of successful executions.

A controlled rollout should also include rollback criteria.

Engineering principle: Evaluate system-level outcomes, not just whether the implemented component behaves correctly.

## 10. Failure modes — What could go wrong with the proposed solution?

This section is about anticipating the consequences of the chosen design.

Suppose bounded admission control is implemented.

What can go wrong?

Failure mode A: Retry amplification

Clients receive overload responses and retry immediately.

```text
High request load
        |
        v
Admission control
        |
        v
Requests rejected
        |
        v
  Clients retry
        |
        v
Even higher load
        |
        +----> Admission control
```

The mitigation might involve exponential backoff, jitter, retry budgets, or client-side rate limiting.

Failure mode B: Head-of-line blocking

A large, expensive query occupies a constrained execution slot while smaller, latency-sensitive queries wait.

A possible mitigation is workload-aware scheduling or separate execution classes.

Failure mode C: Resource-estimation errors

The system admits queries based on estimated memory requirements, but actual usage significantly exceeds estimates.

A possible mitigation is runtime resource enforcement and conservative admission policies.

Failure mode D: Coordinator failure

Admission state lives in a single coordinator. If that coordinator fails, queued queries or admission decisions may be lost or disrupted.

The appropriate response depends on the recovery and durability guarantees.

This is a deeper engineering mindset: a solution should be evaluated not only under expected conditions, but also under unexpected and adverse conditions.

Engineering principle: Every solution introduces assumptions and potential new failure modes.

## 11. The deeper lesson: three distinct kinds of reasoning

The nine sections can be grouped into three larger phases.

### Phase 1 — Understand

```text
Problem -> Constraints -> Hypotheses -> Evidence -> Experiments
```

Determine what is actually happening and what causes it.

### Phase 2 — Decide

```text
Alternatives -> Decision
```

Select a solution based on evidence, requirements, and trade-offs.

### Phase 3 — Verify and anticipate

```text
Validation -> Failure modes -> Reassessment
```

Confirm the decision works and understand the risks it introduces.

These phases are applicable well beyond performance engineering. They work for reliability incidents, architectural redesigns, database migrations, capacity planning, storage designs, and concurrency problems.

## 12. How to practice this skill

The most effective exercise isn't necessarily to build something. It's to take a realistic, underspecified engineering problem and work through the investigation before touching the implementation.

Initially, the quality of the reasoning matters more than finding the correct solution.

A particularly useful habit is to ask, after every hypothesis:

> What observation would prove this hypothesis wrong?

And after every proposed solution:

> Under what circumstances would this solution make the system worse?

Those two questions develop some of the most important skills in engineering: scientific reasoning and trade-off awareness.

The long-term goal is to move from "I know how to implement this" to "I understand why this is the right thing to implement, what evidence supports it, and where it might fail."
