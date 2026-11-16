# Production AI inference

Running a generative AI model and operating a production inference system are fundamentally different engineering problems.

Loading model weights onto a GPU and executing a forward pass proves that a model can generate outputs. It does not guarantee that the system can serve thousands of concurrent requests efficiently, maintain predictable latency, recover from hardware failures, or operate economically.

Production inference requires solving three distinct but interconnected problems:

1. **Runtime:** How efficiently can a model execute on available hardware?
2. **Infrastructure:** How can inference capacity be managed reliably across a distributed fleet?
3. **Tooling:** How can inference systems expose useful abstractions without hiding critical performance controls?

Each layer addresses a different source of complexity.

## 1. Runtime: Making a single inference instance efficient

The runtime is responsible for executing a model efficiently on a GPU-backed instance.

At a high level:

```text
Inference Runtime
-----------------

   Incoming Requests
           |
           v
+---------------------+
| Request Scheduler   |
+---------------------+
           |
           v
+---------------------+
| Batching            |
| KV Cache Manager    |
| Memory Allocator    |
+---------------------+
           |
           v
+---------------------+
| Model Execution     |
| GPU Kernels         |
+---------------------+
           |
           v
+---------------------+
| GPU                 |
|                     |
| Model Weights       |
| KV Cache            |
| Activations         |
+---------------------+
           |
           v
    Generated Tokens
```

The challenge is that **generative inference is not a single fixed computation**.

Unlike a conventional neural network performing one forward pass per request, autoregressive language models generate tokens sequentially.

For example, generating the sentence:

`"The database is unavailable"`

requires multiple dependent execution steps.

```text
    Prompt
      |
      v
   Prefill
      |
      v
    "The"
      |
      v
  "database"
      |
      v
     "is"
      |
      v
"unavailable"
```

**Each generated token depends on the preceding context.**

This creates two distinct phases of execution.

### Prefill versus decode

**Prefill** processes the input prompt and initializes the KV cache. It can exploit substantial parallelism across prompt tokens.

**Decode** generates additional tokens, typically one token per active sequence per decoding iteration.

| Property           | Prefill                      | Decode                                      |
| ------------------ | ---------------------------- | ------------------------------------------- |
| Primary task       | Process input tokens         | Generate output tokens                      |
| Parallelism        | High across prompt positions | Limited across positions within a sequence  |
| Typical bottleneck | Compute throughput           | Memory bandwidth for small batches          |
| Main optimization  | Efficient matrix operations  | Batching, weight reuse, KV-cache efficiency |

The decode phase is particularly challenging.

Consider a model with 70 billion parameters using 16-bit weights.

Its weights alone require approximately 140 GB of memory.

For each decode iteration, the execution engine must access a substantial portion of these weights. With a small batch, relatively little computation is performed per byte of model weights read.

Consequently, GPUs can spend significant time transferring data rather than performing useful arithmetic.

This is a memory-bandwidth problem.

### Why batching matters

Suppose three requests arrive simultaneously:

```text
Request A ---> Generate 100 tokens
Request B ---> Generate  20 tokens
Request C ---> Generate 200 tokens
```

Executing each request independently wastes opportunities to reuse the model weights across requests.

A runtime can instead batch active requests:

```text
GPU Execution
-------------

Iteration   1:  A + B + C
Iteration   2:  A + B + C
                ...
Iteration  20:  A + B + C
Iteration  21:  A + C
                ...
Iteration 100:  A + C
Iteration 101:  C
                ...
Iteration 200:  C
```

This technique is known as **continuous batching** when requests are dynamically admitted and removed between decoding iterations.

Unlike static batching, it does not require all requests to begin and finish together.

The result is typically higher GPU utilization and greater token throughput.

However, larger batches introduce trade-offs:

- Greater memory consumption from active KV caches.
- Potentially higher inter-token latency under saturation.
- More complex admission control and scheduling.
- Increased interference between requests with different prompt and output lengths.

**The runtime must therefore optimize more than raw GPU utilization.**

### The runtime is a resource scheduler

An efficient inference runtime coordinates competing resources:

| Resource             | Primary concern                                         |
| -------------------- | ------------------------------------------------------- |
| GPU compute          | Efficient execution of attention and matrix operations  |
| GPU memory bandwidth | Avoiding repeated expensive memory transfers            |
| GPU memory capacity  | Accommodating weights, KV caches, and temporary buffers |
| CPU                  | Tokenization, scheduling, orchestration                 |
| GPU interconnect     | Communication when execution spans multiple GPUs        |

Optimizations include PagedAttention-style KV-cache management, prefix caching, quantization, fused kernels, speculative decoding, and tensor parallelism.

Many of these optimizations improve one dimension while potentially worsening another.

For example, quantization reduces memory consumption and bandwidth demand, but may introduce additional computation, compatibility constraints, or accuracy degradation.

**Key engineering principle:** A fast inference runtime is not merely a collection of optimized GPU kernels. It is a scheduling and memory-management system that must maximize useful token throughput while satisfying latency and memory constraints.

## 2. Infrastructure: Turning optimized instances into a reliable distributed system

An optimized runtime only solves the problem of executing inference efficiently on a particular machine.

Production systems must coordinate hundreds or thousands of GPU-backed instances while handling traffic variability, failures, capacity constraints, and geographic distribution.

This is a distributed systems problem.

Consider the following architecture:

```text
                      Clients
                         |
                         v
              +---------------------+
              | API Gateway         |
              | Auth / Quotas       |
              +---------------------+
                         |
                         v
              +---------------------+
              | Global Router       |
              +---------------------+
                         |
                         v
          +--------------+--------------+
          |                             |
          v                             v
       Region A                      Region B
          |                             |
          v                             v
 +-----------------+           +-----------------+
 | Admission       |           | Admission       |
 | Control         |           | Control         |
 +-----------------+           +-----------------+
          |                             |
          v                             v
 +-----------------+           +-----------------+
 | Scheduler       |           | Scheduler       |
 +-----------------+           +-----------------+
          |                             |
   +------+------+               +------+------+
   |             |               |             |
   v             v               v             v
 GPU 1         GPU 2           GPU 3         GPU 4
   |             |               |             |
Runtime       Runtime         Runtime       Runtime
```

The infrastructure layer is responsible for making these independent inference instances behave like a reliable service.

### Challenge A: Load balancing is not straightforward

In a conventional HTTP application, routing requests using round-robin or least-connections can work reasonably well.

Inference workloads behave differently.

Two requests might have drastically different resource requirements:

```text
Request A:
  Input:    100 tokens
  Output:    20 tokens

Request B:
  Input: 20,000 tokens
  Output: 2,000 tokens
```

Although each request counts as one HTTP request, their computational costs are very different.

**A scheduler that only considers request counts can produce severe load imbalances.**

Furthermore, an inference request consumes resources over time. The KV cache grows during decoding, and the output length may not be known in advance.

A better scheduling system considers:

- Active decoding sequences.
- Available KV-cache capacity.
- Estimated prefill cost.
- Token generation throughput.
- Request deadlines and priorities.
- Prefix-cache locality.

This introduces an important distinction between **request balancing** and **workload balancing**.

For example:

```text
Naive request balancing:

GPU A: 10 short requests
GPU B: 10 very long requests

Equal request counts
Unequal computational load


Workload-aware balancing:

GPU A: 18 short requests
GPU B:  2 long requests

Unequal request counts
Potentially balanced work
```

The exact distribution depends on model behavior, hardware, batching, and current cache state.

### Challenge B: Scaling GPU capacity is expensive and slow

Conventional stateless services can often scale horizontally by adding relatively lightweight application instances.

Inference replicas have more complicated startup requirements:

```text
 Provision GPU Instance
           |
           v
   Initialize Runtime
           |
           v
   Load Model Weights
           |
           v
Initialize GPU Resources
           |
           v
   Warm Up Execution
           |
           v
    Accept Requests
```

Loading hundreds of gigabytes of model weights can make cold starts expensive.

Additionally, GPU capacity is not always immediately available. It may be constrained by hardware availability, regional placement, quotas, or cloud-provider capacity.

This makes reactive autoscaling harder.

Suppose traffic suddenly doubles.

**The system cannot necessarily double its inference capacity instantly.**

Instead, it may have to:

1. Use existing spare capacity.
2. Queue some requests.
3. Apply admission control or load shedding.
4. Provision additional GPU instances.
5. Shift eligible traffic to other regions or clusters.

This resembles capacity management in other distributed systems, but with unusually expensive resources and significant startup costs.

### Challenge C: Reliability must account for stateful execution

Although the model weights are typically immutable during inference, active inference requests maintain temporary state.

That state includes the KV cache and the position within a partially generated sequence.

**If a GPU fails halfway through generating a response, another GPU generally cannot simply resume execution unless the necessary state is available or recoverable.**

```text
GPU A
  |
  +-- Model Weights
  |
  +-- KV Cache
  |
  +-- Request: 150 tokens generated
  |
  X  GPU Failure
  |
  v
Request Interrupted
```

Possible recovery strategies include restarting generation, reconstructing state from the original prompt and generated tokens, or using more sophisticated state-transfer or replicated-state mechanisms.

Each strategy has different costs.

Recomputation consumes GPU resources, while state transfer introduces communication overhead and additional engineering complexity.

This is why high availability in inference requires more than running multiple replicas.

The system must consider what happens to **in-flight generations** during failures.

### Challenge D: Avoiding capacity silos

A capacity silo occurs when GPU resources are partitioned into isolated pools that cannot efficiently share demand.

For example:

```text
                 GPU Fleet

Region A              Region B
--------              --------

Capacity: 100         Capacity: 100
Demand:   130         Demand:    40

Overloaded            Underutilized
```

Globally, the fleet has enough aggregate capacity for the 170 units of demand.

However, Region A is overloaded because capacity in Region B is not available to serve its requests.

A global routing layer can improve utilization by redirecting eligible traffic.

But this introduces trade-offs involving network latency, data residency, failure domains, and the cost of interregional communication.

**Key engineering principle:** Inference infrastructure must optimize global resource utilization without allowing resource sharing to undermine latency isolation, reliability, or availability.

## 3. Tooling: Balancing abstraction and engineering control

The third layer addresses a different problem: how inference capabilities are exposed to engineers.

An inference platform can be extremely efficient internally but still difficult to operate if every application team must understand GPU allocation, batching algorithms, memory management, and deployment orchestration.

At one extreme, every team manages the entire inference stack.

```text
    Application Team
           |
           v
Implement Model Serving
           |
           v
  Implement Scheduling
           |
           v
  Manage GPU Resources
           |
           v
  Configure Networking
           |
           v
 Monitor Infrastructure
```

This gives maximum control but creates substantial duplication and operational complexity.

At the opposite extreme, a platform exposes a simple API while hiding all implementation details.

```text
      Application
           |
           v
+---------------------+
| Inference API       |
|                     |
| generate(prompt)    |
+---------------------+
           |
           v
Managed Inference System
```

This greatly improves productivity.

However, an overly restrictive abstraction can prevent engineers from controlling performance-critical behavior.

For example, an application serving interactive chat requests may require different scheduling and latency settings than one processing millions of documents asynchronously.

A useful platform exposes **high-level abstractions with selective low-level controls**.

### The right abstraction boundary

Consider three levels of control:

| Level       | Controls                                                     | Typical responsibility |
| ----------- | ------------------------------------------------------------ | ---------------------- |
| Application | Model choice, maximum output tokens, latency priority        | Product requirements   |
| Deployment  | Replica counts, GPU type, quantization, autoscaling policies | Capacity and cost      |
| Runtime     | Batch scheduling, KV-cache policies, kernel selection        | Execution efficiency   |

A good platform provides sensible defaults while allowing advanced configuration where necessary.

Examples include:

- Request priorities and latency objectives.
- Model deployment and versioning.
- Throughput versus latency configurations.
- Resource quotas and capacity limits.
- Profiling, observability, and debugging.
- Rollouts, rollbacks, and evaluation workflows.

The challenge is exposing enough control to optimize workloads without requiring every engineer to understand every internal implementation detail.

This reflects a general systems-engineering principle:

**An abstraction should hide incidental complexity, not the controls necessary to achieve system-level requirements.**

## 4. Why the three layers cannot be optimized independently

The most interesting engineering problems arise at the boundaries between layers.

Consider an infrastructure scheduler attempting to improve load balancing.

Suppose the scheduler observes:

```text
GPU A:
  70% utilization

GPU B:
  40% utilization
```

A conventional load balancer might conclude that GPU B should receive the next request.

However, suppose GPU A already holds a cached prefix for that request's prompt.

Routing the request to GPU A could avoid redundant prefill computation.

```text
                   Incoming Request
                          |
                          v
                   Global Scheduler
                          |
                          v
           +--------------+--------------+
           |                             |
           v                             v
+---------------------+       +---------------------+
| GPU A               |       | GPU B               |
| Utilization: 70%    |       | Utilization: 40%    |
| Prefix: Cached      |       | Prefix: Missing     |
+---------------------+       +---------------------+
           |                             |
           v                             v
     Reuse KV Cache               Compute Prefill
```

Now the scheduling decision depends on two layers:

- **Runtime:** Knows which prefixes are cached and how much KV-cache memory remains.
- **Infrastructure:** Knows the load, availability, and network locality of candidate replicas.

**A decision based solely on GPU utilization may be suboptimal.**

Likewise, routing everything to the replica with the best prefix-cache hit rate may overload that replica and degrade latency.

**The optimal routing decision balances these competing costs.**

This is a common principle in distributed systems: **local optimization does not necessarily produce global optimization.**

### Another example: Autoscaling versus batching

Suppose a workload experiences increasing request concurrency.

The infrastructure detects higher load and adds replicas.

That sounds beneficial, but there is a subtle interaction.

If the additional replicas distribute requests too thinly, each runtime might operate with smaller batches.

Smaller batches can reduce GPU efficiency because there is less work over which to amortize model-weight reads.

```text
Before Scaling:

GPU A: Batch = 64
GPU B: Batch = 64

After Scaling:

GPU A: Batch = 32
GPU B: Batch = 32
GPU C: Batch = 32
GPU D: Batch = 32
```

Depending on the workload, the system may trade higher total capacity and lower queueing delay for lower efficiency per GPU.

This is not necessarily bad. In fact, it can improve user-facing latency.

But it demonstrates why maximizing utilization and minimizing latency are different objectives.

## 5. What does good inference performance actually mean?

Inference performance must be evaluated across several dimensions.

| Metric                  | Meaning                                                      | Primary concern     |
| ----------------------- | ------------------------------------------------------------ | ------------------- |
| TTFT                    | Time to first token                                          | Responsiveness      |
| TPOT                    | Time per output token                                        | Streaming speed     |
| Throughput              | Generated tokens per second                                  | Processing capacity |
| Goodput                 | Useful work completed within specified service objectives    | Effective capacity  |
| GPU utilization         | How busy GPU execution resources are                         | Resource efficiency |
| Cost per million tokens | Infrastructure cost normalized by output                     | Economics           |
| Availability            | Fraction of time the service can successfully serve requests | Reliability         |

These metrics can conflict.

For example, increasing batch size often improves aggregate throughput but may increase latency for individual requests.

Provisioning more GPUs may reduce latency but increase cost per token if many instances remain underutilized.

A runtime can achieve excellent benchmark throughput while the overall service suffers from poor routing decisions, slow autoscaling, or excessive queueing.

The actual engineering goal is closer to:

```text
Maximize useful throughput
```

subject to:

```text
P99(latency) <= SLO
```

```text
Memory consumption <= GPU capacity
```

```text
Availability >= Availability target
```

and acceptable operating cost.

**In practice, TTFT and TPOT often require separate latency objectives, especially for streaming workloads.**

## 6. The complete architecture

The three layers fit together as follows:

```text
+------------------------------------------------------+
|                       TOOLING                        |
|                                                      |
|  Deployment APIs                                     |
|  Model Configuration                                 |
|  Performance Profiling                               |
|  Monitoring and Debugging                            |
|  Rollouts and Version Management                     |
+------------------------------------------------------+
                           |
                           v
+------------------------------------------------------+
|                    INFRASTRUCTURE                    |
|                                                      |
|  Global Traffic Routing                              |
|  Load Balancing                                      |
|  Autoscaling                                         |
|  Admission Control                                   |
|  Capacity Management                                 |
|  Failure Recovery                                    |
|  Multi-Region / Multi-Cluster Orchestration          |
+------------------------------------------------------+
                           |
                           v
+------------------------------------------------------+
|                       RUNTIME                        |
|                                                      |
|  Request Scheduling                                  |
|  Continuous Batching                                 |
|  KV Cache Management                                 |
|  Prefill / Decode                                    |
|  GPU Memory Management                               |
|  GPU Kernel Execution                                |
+------------------------------------------------------+
                           |
                           v
+------------------------------------------------------+
|                       HARDWARE                       |
|                                                      |
|  GPU Compute                                         |
|  HBM Capacity and Bandwidth                          |
|  GPU Interconnects                                   |
|  CPU / RAM / Networking                              |
+------------------------------------------------------+
```

Each layer has a fundamental optimization objective:

- **Runtime:** Execute the greatest amount of useful inference work per unit of hardware while meeting latency constraints.
- **Infrastructure:** Allocate and coordinate inference resources across a distributed fleet while preserving reliability and efficiency.
- **Tooling:** Make sophisticated inference capabilities accessible, controllable, observable, and maintainable.

## 7. The broader engineering lesson

Production inference combines several well-established disciplines:

**Performance engineering:** Understanding arithmetic intensity, memory bandwidth, GPU utilization, and latency.

**Operating systems:** Managing memory, scheduling work, allocating scarce resources, and isolating competing workloads.

**Distributed systems:** Coordinating resources, managing failures, balancing demand, and maintaining availability.

**Platform engineering:** Providing abstractions, deployment workflows, observability, and operational controls.

What makes inference distinctive is the tight coupling between these disciplines.

A routing decision affects batching. Batching affects memory consumption. Memory consumption affects admission control. Admission control affects tail latency. Tail latency determines whether the distributed service meets its objectives.

The central architectural principle is that **inference efficiency is an end-to-end property, not merely a GPU execution property**.

Optimizing model execution is necessary, but achieving reliable, low-latency, economically efficient inference requires coordinating the runtime, infrastructure, and tooling as one system.
