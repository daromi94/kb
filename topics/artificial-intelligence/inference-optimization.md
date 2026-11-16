# Inference optimization

Inference engineering is fundamentally about **allocating finite computational resources to deliver the best possible application experience**.

The challenge is that inference performance cannot be described by a single metric.

A system can achieve extremely high throughput while producing unacceptable response latency. It can generate responses quickly while degrading output quality. It can offer excellent latency and quality while being economically unsustainable.

Consequently, optimizing inference requires understanding the relationships among three fundamental dimensions:

- **Latency:** How quickly does the system respond?
- **Throughput:** How much work can the system process?
- **Quality:** How good are the generated outputs?

**These dimensions interact, and improving one can worsen another.**

## 1. Why inference optimization is not simply maximizing GPU performance

Consider an inference server running a language model.

A straightforward optimization objective might be:

> Maximize the number of generated tokens per second.

However, suppose the server handles an interactive coding assistant.

A configuration that generates 10,000 tokens per second in aggregate but makes individual requests wait several seconds before receiving the first token might be unsuitable.

Conversely, a configuration delivering exceptionally low latency to individual requests might waste GPU capacity because it executes requests in very small batches.

**The correct objective depends on the application.**

### Three different workloads

| Workload                    | Primary objective      | Secondary concerns         |
| --------------------------- | ---------------------- | -------------------------- |
| Interactive chatbot         | Low latency            | Quality, concurrency, cost |
| Offline document processing | High throughput        | Quality, cost              |
| Coding agent                | High task success rate | End-to-end latency, cost   |

The same model, GPU, and runtime may require different configurations for each workload.

For example, an offline document-processing service can accumulate requests into large batches because immediate responses are unnecessary.

An interactive chatbot usually cannot tolerate the same waiting behavior.

**The first principle of inference optimization is that performance must be defined in terms of application requirements, not hardware capabilities alone.**

## 2. Latency: how long does inference take?

Latency measures how long an operation takes.

However, generative inference has multiple latency components.

A simplified request lifecycle looks like this:

```text
  Request Arrives
         |
         v
+------------------+
| Queueing         |
+------------------+
         |
         v
+------------------+
| Prefill          |
+------------------+
         |
         v
+------------------+
| Decode           |
+------------------+
         |
         v
 Response Complete
```

Three important metrics capture different aspects of the experience.

### Time to first token (TTFT)

TTFT measures the time between submitting a request and receiving the first generated token.

It includes queueing, preprocessing, prefill, and initial generation overhead.

For interactive applications, TTFT often determines perceived responsiveness.

### Time per output token (TPOT)

TPOT measures the average time between generated tokens during decoding.

For streaming responses, it determines how smoothly text appears.

### End-to-end latency (E2E)

End-to-end latency measures the total time required to complete a response.

A simplified approximation is:

```text
T_total ~= TTFT + (N - 1) * TPOT
```

where `N` is the number of generated tokens.

**The important observation is that optimizing TTFT and optimizing TPOT are not necessarily the same problem.**

For example, prioritizing prefill operations can improve TTFT while delaying decoding for requests already generating tokens.

This creates a scheduling trade-off.

## 3. Throughput: how much work can the system process?

Throughput measures work completed per unit of time.

For inference, common throughput metrics include:

- Requests per second.
- Input tokens processed per second.
- Output tokens generated per second.

These metrics measure different things.

A server generating 10,000 output tokens per second could be processing 100 requests producing 100 tokens each or 10 requests producing 1,000 tokens each.

The aggregate token throughput might be identical, but the scheduling and memory requirements can differ substantially.

### Why batching improves throughput

Consider a GPU that must repeatedly read model weights during decoding.

Without batching:

```text
GPU
 |
 +-- Read Model Weights --> Decode A
 |
 +-- Read Model Weights --> Decode B
 |
 +-- Read Model Weights --> Decode C
```

With batching:

```text
GPU
 |
 +-- Read Model Weights
           |
           +-- Decode A
           +-- Decode B
           +-- Decode C
```

This is a simplified illustration of weight reuse within a batched execution.

By processing multiple requests together, the runtime amortizes memory traffic and increases arithmetic intensity.

For many decode workloads, batching substantially improves GPU efficiency.

But batching introduces another problem.

### Throughput versus latency

Suppose a server waits to accumulate a batch before executing it.

A larger batch can improve aggregate throughput, but requests may spend more time waiting.

Additionally, the GPU must process more active sequences per iteration, which can increase iteration duration.

The resulting relationship often looks like this:

```text
Small batches:
  Lower batching delay
  Lower aggregate throughput

Medium batches:
  Good throughput
  Acceptable latency

Large batches:
  High aggregate throughput
  Potentially worse latency
  Greater memory requirements
```

**Continuous batching reduces the need to wait for fixed batches, but it does not eliminate contention for GPU compute, memory bandwidth, and KV-cache capacity.**

### Queueing makes the trade-off more severe

Let:

- **`lambda`** = arrival rate, measured in requests per second.
- **`mu`** = sustainable service capacity, measured in requests per second.

As offered load approaches service capacity, queueing delay can increase dramatically.

A simple M/M/1 model illustrates the effect:

```text
W = 1 / (mu - lambda)
```

**`W` is the mean time in the system, including both waiting and service.** This formula assumes Poisson arrivals, exponential service times, one server, and `lambda < mu`. Actual inference systems use batched, variable-duration GPU execution and have more complicated queueing behavior, but the qualitative principle remains valuable.

The implications are significant:

A GPU operating at maximum sustainable throughput may have insufficient spare capacity to absorb bursts without causing substantial queueing.

Thus, **maximum throughput is not necessarily maximum useful throughput**.

## 4. Quality: faster inference can produce worse outputs

Quality represents how well the generated output satisfies the application's requirements.

Depending on the workload, quality may mean:

- Answer correctness.
- Code generation success.
- Reasoning accuracy.
- Instruction-following performance.
- Output consistency.
- Task completion rate.

Several inference optimizations affect quality.

### Example: quantization

Quantization represents model parameters using reduced numerical precision.

For example:

```text
   FP16 Weights
        |
        | Quantization
        v
INT8 / INT4 Weights
```

Lower precision can reduce memory usage and memory-bandwidth pressure.

This may allow larger models to fit on available hardware or improve execution speed.

However, quantization introduces approximation error.

Depending on the model, quantization method, and task, that error may affect output quality.

The trade-off becomes:

```text
Reduced Precision
        |
        +--> Lower Memory Usage
        |
        +--> Potentially Faster Execution
        |
        +--> Potential Accuracy Degradation
```

Importantly, quantization does not always improve speed, and quality degradation is not inevitable. Both must be measured.

### Example: choosing a smaller model

Suppose two models are available.

| Property               | Model A             | Model B             |
| ---------------------- | ------------------- | ------------------- |
| Parameters             | 8 billion           | 70 billion          |
| Memory requirements    | Lower               | Higher              |
| Typical inference cost | Lower               | Higher              |
| Potential task quality | Depends on workload | Depends on workload |
| Serving complexity     | Lower               | Higher              |

Model A may be faster and cheaper.

Model B may perform better on difficult reasoning tasks.

But using Model B for every request could be economically inefficient.

A useful architecture is model routing:

```text
            Incoming Request
                   |
                   v
         +-------------------+
         | Task Classifier   |
         +-------------------+
                   |
     +-------------+-------------+
     |                           |
     v                           v
Simple Task                 Complex Task
     |                           |
     v                           v
Small Model                 Large Model
     |                           |
     +-------------+-------------+
                   |
                   v
                 Output
```

The difficulty is accurately identifying which requests require the larger model.

Routing errors may increase latency, cost, or quality failures.

The best system may therefore use multiple models rather than optimizing one model in isolation.

## 5. The Pareto frontier: why there is no universally best configuration

The central mathematical concept behind multi-objective optimization is **Pareto optimality**.

**A configuration is Pareto-optimal if no other available configuration improves one objective without worsening at least one other objective.**

Suppose three inference configurations are measured:

| Configuration | P99 latency | Throughput  | Quality score |
| ------------- | ----------- | ----------- | ------------- |
| A             | 100 ms      | 1,000 tok/s | 85%           |
| B             | 180 ms      | 2,500 tok/s | 85%           |
| C             | 300 ms      | 3,200 tok/s | 92%           |

Hypothetical measurements illustrating competing objectives, not benchmark results.

Which configuration is best?

There is no universal answer.

Configuration A minimizes latency.

Configuration B provides greater throughput without reducing the measured quality.

Configuration C provides the highest measured throughput and quality, but has the highest latency.

All three can be rational choices depending on application requirements.

A fourth configuration with 250 ms latency, 2,000 tokens per second, and 80% quality would be dominated by B, because B is better in every measured dimension.

The practical goal is to select the best point on the Pareto frontier that satisfies application constraints.

## 6. From maximum throughput to goodput

One of the most useful concepts in production inference is **goodput**.

Throughput measures how much work is processed.

**Goodput measures how much useful work satisfies the application's performance objectives.**

Suppose two inference configurations are evaluated.

| Metric                       | Configuration A | Configuration B |
| ---------------------------- | --------------- | --------------- |
| Completed requests/sec       | 120             | 100             |
| Requests meeting latency SLO | 70%             | 98%             |
| Goodput                      | 84 req/s        | 98 req/s        |

Configuration A achieves higher raw throughput.

However, Configuration B completes more requests within the latency objective.

Therefore, Configuration B delivers better goodput.

Formally, for a fixed observation window:

```text
Goodput = Requests satisfying all required SLOs / Elapsed time
```

Goodput can incorporate latency, quality, and correctness requirements.

For example, a request might count as useful only if:

```text
TTFT <= 500 ms
```

```text
TPOT <= 50 ms
```

```text
Quality requirements satisfied
```

This changes the optimization target from generating as many tokens as possible to completing as much valuable work as possible.

## 7. Optimization should be expressed as a constrained problem

Instead of saying:

> Make inference as fast as possible.

A useful engineering objective is:

> Minimize inference cost while maintaining application quality and latency targets at the expected traffic load.

Mathematically:

```text
min_theta Cost(theta)
```

subject to:

```text
P99(TTFT(theta)) <= 500 ms
```

```text
P99(TPOT(theta)) <= 50 ms
```

```text
Q(theta) >= Q_min
```

```text
Goodput(theta) >= G_min
```

Here, `theta` represents the complete inference configuration, potentially including:

- Model selection.
- GPU type and count.
- Quantization method.
- Batch scheduling policy.
- KV-cache allocation.
- Request routing policy.
- Replica placement and autoscaling.

**A configuration is only valid if it satisfies the constraints.**

Among valid configurations, the optimization process selects the one with the lowest cost.

This is a much more precise problem than simply maximizing GPU utilization.

## 8. The engineering implications

Several important principles follow from this approach.

**Optimization requires workload characterization.** An inference system cannot be optimized effectively without understanding prompt lengths, output lengths, request arrival patterns, concurrency, and quality requirements.

**Performance is evaluated at the application boundary.** GPU kernel speed is useful, but end-to-end response latency and task success are what ultimately matter.

**Scheduling policies encode product priorities.** Prefill prioritization, continuous batching, admission control, and request routing determine which requests receive resources and when.

**Resource utilization is not the ultimate goal.** Running a GPU at 100% utilization is not inherently desirable if request latency becomes unacceptable.

**Quality must be measured, not assumed.** Techniques such as quantization, model routing, and speculative decoding require workload-specific validation.

**The optimization target changes with the workload.** Interactive generation, batch processing, and long-running agents operate under different constraints.

The key distinction is:

```text
Naive Optimization
------------------

    Maximize GPU Utilization
               |
               v
   Maximize Token Throughput


Production Optimization
-----------------------

 Define Application Objectives
               |
               v
     Characterize Workload
               |
               v
Establish Latency / Quality SLOs
               |
               v
Evaluate Runtime Configurations
               |
               v
    Find Feasible Trade-offs
               |
               v
Maximize Goodput / Minimize Cost
```

**The fundamental lesson:** Inference engineering is not about making models execute as fast as possible in isolation. It is about making the entire serving system deliver the greatest amount of useful, high-quality work under latency, capacity, reliability, and economic constraints.
