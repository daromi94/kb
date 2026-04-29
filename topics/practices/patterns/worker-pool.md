# Worker pool

A concurrency pattern: spin up a fixed number of long-lived workers that pull
tasks from a shared queue, instead of spawning a new thread or process for
every unit of work. The pool size caps concurrency — with 8 workers, at most
8 tasks run in parallel, regardless of how many are pending.

## Why use it

Spawning per-task is fine when work is rare. Once requests arrive faster
than they finish, unbounded spawning floods the system: blowing past CPU
cores, exhausting memory, saturating file descriptors, or hammering a
downstream database with too many connections.

A pool gives one knob — pool size — that bounds all of that. It also
amortizes worker setup cost (thread creation, connection handshakes) across
many tasks.

## Components

| Part       | Role                                                       |
|------------|------------------------------------------------------------|
| Task queue | Buffer (usually FIFO) holding tasks until a worker is free |
| Workers    | Fixed set of threads/processes looping over the queue      |
| Dispatcher | Producer pushing tasks into the queue                      |
| Results    | Optional queue for returning answers to callers            |
| Shutdown   | Signal so workers exit cleanly when the program is done    |

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
until memory is exhausted — failure shows up as OOM rather than a visible
saturation signal. A bounded queue forces a deliberate decision when full:
block the producer, drop, or reject.

**Choose a rejection policy.** Standard options are abort (reject with
error), caller-runs (the producer executes the task itself, providing
natural backpressure), drop-oldest, and drop-newest. Caller-runs is the
canonical backpressure trick; drop policies hide overload and must be a
conscious choice.

**Size for the workload type.** CPU-bound work wants roughly $N = cores$.
I/O-bound work follows $N = cores \times utilization \times (1 + W/C)$,
where $W/C$ is the wait-to-compute ratio. Don't pick a thread count by
intuition — measure the ratio.

**One pool per workload class (bulkhead).** Mixing heterogeneous tasks
lets a slow or misbehaving dependency saturate workers needed by healthy
ones, stalling unrelated work. Separate pools by latency profile and
criticality — blocking I/O calls, CPU work, and request handlers each
get their own.

**Never let a pooled task wait on another task in the same pool.**
Dependent tasks fill all workers, then wait for subtasks that can never
be scheduled — thread-starvation deadlock. Run dependent stages on a
separate pool, or restructure into non-blocking composition (futures,
callbacks, pipelines).

**Don't let exceptions silently kill workers.** An uncaught error can
terminate a worker; even when the pool spawns a replacement, the failure
goes unlogged. Catch and log inside each task body, and hook into the
pool's task-completion callback if one is provided. Failures captured
inside result futures are invisible until someone reads them — log on
the worker side too.

**Make tasks cancellation-aware and bound their runtime.** Cancellation
delivers a signal (a flag, context, or token); a task that never checks
runs to completion regardless. A stuck task ties up a worker forever and
eventually starves the pool. Apply per-task timeouts, and ensure
blocking calls inside tasks honor cancellation.

**Reset thread-local state between tasks.** Pooled threads are reused,
so any thread-local variable (logging context, security context, mutable
cache) leaks from one task into the next — a classic source of
cross-tenant bugs. Avoid thread-locals in pooled code, or clear them in
a cleanup step that runs whether the task succeeded or failed.

**Shut down in two phases.** First stop accepting new work and let
in-flight tasks drain with a deadline; then force-stop any stragglers
and discard the queued remainder. Single-phase shutdowns either lose
pending work or hang forever on a stuck task.

**Instrument queue-wait time, not just throughput.** A pool can be
saturated long before CPU shows it; the symptom is queueing latency.
Export queue depth, active workers, submission rate, execution time,
queue-wait time, and rejection count. p99 queue-wait is the leading
indicator of saturation.

## Trade-offs

| Benefit                             | Cost                                       |
|-------------------------------------|--------------------------------------------|
| Bounded resource use under load     | Sizing requires measurement, not intuition |
| Amortized worker setup cost         | Adds queueing latency at saturation        |
| Natural backpressure point          | Risk of starvation deadlock if tasks nest  |
| One place to instrument concurrency | Reused workers leak thread-local state     |

## Common applications

**Request handlers.** Web servers, RPC servers, and message brokers fan
out incoming work to a fixed-size pool sized for downstream-call latency.

**Batch processing.** Files, URLs, jobs from a queue — independent units
of work pulled by reusable workers.

**Network resiliency.** Bulkhead pools per downstream dependency cap
blast radius when one slows or fails.

Less useful when tasks have complex interdependencies — reach for a
DAG executor or actor model instead.

---

Return to [Patterns](_index.md)
