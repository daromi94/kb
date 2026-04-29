# Worker pool

A concurrency pattern: a fixed number of long-lived workers share a queue
and pull tasks from it, instead of spawning a fresh thread or process for
every unit of work. Pool size sets the concurrency cap — eight workers
means at most eight tasks run in parallel, no matter how many are pending.

## Why use it

Per-task spawning is fine when work is rare. Once tasks arrive faster than
they complete, unbounded spawning floods the system — blowing past CPU
cores, exhausting memory, saturating file descriptors, or hammering a
downstream database with too many connections.

A pool exposes a single knob — pool size — that bounds the whole problem.
It also amortizes worker setup cost (thread creation, connection
handshakes) across many tasks rather than paying it per call.

## Components

| Part       | Role                                                       |
|------------|------------------------------------------------------------|
| Task queue | Buffer (usually FIFO) holding tasks until a worker is free |
| Workers    | Fixed set of threads or processes looping over the queue   |
| Dispatcher | Producer that pushes tasks into the queue                  |
| Results    | Optional return path for answers back to callers           |
| Shutdown   | Signal that lets workers exit cleanly on program exit      |

## Flow

```
producer --> [ task queue ] --> worker 1 --+
                            --> worker 2 --+--> [ results ]
                            --> worker N --+
```

## Pseudocode

```text
function worker(tasks):
    while task = tasks.take(): # blocks until task arrives or queue closes
        process(task)

class Pool:
    constructor(size, queueCapacity):
        this.tasks = BoundedQueue(queueCapacity)
        for i in 0..size:
            spawn worker(this.tasks)

    submit(task):
        this.tasks.put(task) # blocks if queue is full

    shutdown():
        this.tasks.close() # workers drain, then exit
        waitAll(workers)

# usage
pool = new Pool(size: 8, queueCapacity: 100)

for task in incoming:
    pool.submit(task)

pool.shutdown()
```

## Design guidelines

**Bound the queue.** An unbounded queue silently absorbs producer overload
until memory runs out, so failure surfaces as an OOM rather than a clear
saturation signal. A bounded queue forces an explicit choice when full:
block the producer, drop tasks, or reject them outright.

**Choose a rejection policy.** Four standard options exist: abort returns
an error to the caller; caller-runs makes the producer execute the task
itself, throttling submission naturally; drop-oldest and drop-newest
discard tasks. Caller-runs is the canonical backpressure mechanism. Drop
policies hide overload, so reach for them only when losing work is
actually acceptable.

**Size for the workload type.** CPU-bound work wants roughly $N = cores$
— extra threads only buy context-switch overhead. I/O-bound work follows
$N = cores \times utilization \times (1 + W/C)$, where $W/C$ is the
wait-to-compute ratio. Don't pick a thread count by intuition; measure
the ratio.

**One pool per workload class (bulkhead).** When heterogeneous tasks
share a pool, a single slow or failing dependency can saturate every
worker and stall unrelated traffic. Give each workload class its own
pool — blocking I/O, CPU work, and request handlers should not compete
for the same threads.

**Never let a pooled task wait on another task in the same pool.**
Dependent tasks can fill every worker and then wait on subtasks that
can never be scheduled — thread-starvation deadlock. Push downstream
stages onto a separate pool, or compose them non-blockingly with
futures, callbacks, or pipelines.

**Don't let exceptions silently kill workers.** An uncaught error can
take its worker down with it. Even if the pool spawns a replacement,
the original failure leaves no trace. Catch and log inside every task
body, and hook into the pool's task-completion callback when one is
exposed. Errors captured inside result futures stay invisible until
someone reads the future — log on the worker side too, not only at
the consumer.

**Make tasks cancellation-aware and bound their runtime.** Cancellation
delivers a signal — a flag, context, or token — that the task must
check. A task that never reads it runs to completion regardless. One
stuck task ties up a worker forever, and a handful of stuck tasks
starve the pool. Apply per-task timeouts, and make sure blocking calls
inside tasks honor the cancellation signal.

**Reset thread-local state between tasks.** Pooled threads are reused
across tasks, so any thread-local state (logging context, security
context, mutable cache) leaks from one task into the next — a classic
source of cross-tenant bugs. Avoid thread-locals in pooled code, or
clear them in a cleanup step that runs whether the task succeeded or
failed.

**Shut down in two phases.** First stop accepting new submissions and
let in-flight tasks drain against a deadline. Then force-stop any
stragglers and discard the queue's remainder. Single-phase shutdowns
either drop pending work or hang forever on one stuck task.

**Instrument queue-wait time, not just throughput.** A pool can be
saturated long before CPU usage shows it; the early symptom is
queueing latency. Export queue depth, active worker count, submission
rate, execution time, queue-wait time, and rejection count. p99
queue-wait is the leading indicator of trouble.

## Trade-offs

| Benefit                             | Cost                                       |
|-------------------------------------|--------------------------------------------|
| Bounded resource use under load     | Sizing requires measurement, not intuition |
| Amortized worker setup cost         | Adds queueing latency at saturation        |
| Natural backpressure point          | Risk of starvation deadlock if tasks nest  |
| One place to instrument concurrency | Reused workers leak thread-local state     |

## Common applications

**Request handlers.** Web servers, RPC servers, and message brokers
dispatch incoming work to a fixed-size pool tuned for downstream-call
latency.

**Batch processing.** Independent units of work — files, URLs, queued
jobs — pulled steadily by a fixed crew of reusable workers.

**Network resiliency.** A separate bulkhead pool per downstream
dependency contains the blast radius when one slows or fails.

Less useful when tasks have rich interdependencies — reach for a DAG
executor or actor model instead.

---

Return to [Patterns](_index.md)
