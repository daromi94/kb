# Context deep dive

A detailed look at the Context API internals, scope lifecycle,
in-process thread propagation, inter-process propagation via
TextMapPropagator, W3C Trace Context headers, and Baggage.

## Context internals

Context is an immutable key-value store that carries execution-scoped
values — the active Span, Baggage entries, and any user-defined
state — along a request's execution path. Each write operation returns
a new Context instance; the original is unchanged.

Context entries are keyed by ContextKey instances. Each signal defines
its own key — the tracing API stores the active Span under one key,
the Baggage API under another. This keeps concerns separated within a
single Context object. Application code can also register custom keys
to propagate domain-specific values.

```java
// Define a custom context key
private static final ContextKey<String> TENANT_KEY = ContextKey.named("tenant-id");

// Store a value — returns a new Context
Context updated = Context.current().with(TENANT_KEY, "acme-corp");

// Retrieve later
String tenant = updated.get(TENANT_KEY);
```

### Thread-local storage

The default ContextStorage binds the active Context to the current
thread via a ThreadLocal. `Context.current()` retrieves the active
Context for the calling thread; if none has been set, it returns the
root (empty) Context.

The storage is pluggable via Java's ServiceLoader. Alternative
ContextStorage implementations exist for:

- **Reactor / RxJava** — store Context in the reactive subscriber
  chain rather than a ThreadLocal, since reactive operators may
  execute across many threads
- **Virtual threads** — prevent pinning of carrier threads that can
  occur when ThreadLocal-based storage interacts with synchronized
  blocks in context propagation code

The pluggability means the rest of the API and instrumentation is
storage-agnostic — it always calls `Context.current()` and the
storage backend decides where to look.

## Scope lifecycle

A Span exists but is invisible to instrumentation until it is made
the *current* Span on the executing thread. Making a Span current
means installing its Context as the thread-local Context so that
`Span.current()` and `Context.current()` discover it.

`Span.makeCurrent()` performs this installation and returns a Scope.
Under the hood, it calls `Context.current().with(span)` to create a
new Context containing the Span, then calls
`newContext.makeCurrent()` on the Context itself, which pushes it onto
the ContextStorage and returns a Scope that will pop it on close.

```java
Span span = tracer.spanBuilder("process-order").startSpan();

try (Scope scope = span.makeCurrent()) {
    // Span.current() == span
    // Any spans created here automatically parent under 'span'
    chargePayment();
    shipOrder();
} finally {
    span.end();
}
```

Closing the Scope restores the previous Context on the ThreadLocal.
This enables correct nesting — an inner span activates, does work,
closes its Scope (restoring the outer span's Context), and the outer
span continues as current.

### Failure modes when scope is not closed

- The Span remains "current" on the thread. Subsequent unrelated
  operations on the same thread (common with thread pools) parent
  under the leaked Span, creating a corrupted trace tree.
- The previous Context is never restored, so the parent Span becomes
  unreachable via `Span.current()` for the remainder of the thread's
  execution in that request.
- The SDK detects this and logs a warning:
  `"Scope.close() was not called"` with a stack trace pointing to
  where `makeCurrent()` was invoked.

## In-process propagation

The most common observability failure in Java is context loss across
thread boundaries. When work is submitted to an ExecutorService,
CompletableFuture, or reactive pipeline, the receiving thread has its
own ThreadLocal — which starts empty or holds a different request's
Context.

### Manual transfer

The Context API provides wrapping methods that snapshot the current
Context at submission time and restore it at execution time:

```java
// Wrap a Runnable — context captured at wrap() time
executor.submit(Context.current().wrap(() -> {
    // Context.current() returns the captured context
    // Span.current() returns the span that was active at wrap()
    doAsyncWork();
}));
```

`Context.current().wrap(Runnable)` and
`Context.current().wrap(Callable)` are the two variants. The wrapper
calls `context.makeCurrent()` before the delegate runs and closes the
Scope afterward, so the borrowed thread's prior Context is restored
after the task completes.

For CompletableFuture chains, each stage may execute on a different
thread. Without wrapping, only the first stage inherits context:

```java
Context ctx = Context.current();

CompletableFuture
    .supplyAsync(ctx.wrap(() -> fetchOrder()), executor)
    .thenApplyAsync(ctx.wrap(order -> validate(order)), executor)
    .thenAcceptAsync(ctx.wrap(order -> persist(order)), executor);
```

There is also `Context.taskWrapping(Executor)`, which returns a
wrapped Executor that automatically applies `Context.current().wrap()`
to every submitted task — useful when you control executor creation
but not every submission site:

```java
Executor traced = Context.taskWrapping(originalExecutor);

traced.execute(() -> {
    // Context automatically propagated
});
```

### Automatic transfer via the Java agent

The OpenTelemetry Java Agent instruments standard concurrency
libraries via bytecode injection. When a Runnable or Callable is
submitted to an ExecutorService, the agent's instrumentation:

1. Captures `Context.current()` on the submitting thread
2. Attaches the captured Context to the task object
3. Calls `context.makeCurrent()` before the task's `run()` executes
4. Closes the Scope after `run()` completes

This covers ExecutorService, ForkJoinPool, ScheduledExecutorService,
and CompletableFuture out of the box. For libraries with custom async
models (Netty's EventLoop, Vert.x, etc.), the agent ships dedicated
instrumentation modules.

The agent approach eliminates manual wrapping entirely but requires
running with `-javaagent`. For environments where an agent is not
viable (e.g., native images, restrictive containers), the manual API
or library-specific instrumentation must be used.

## Inter-process propagation

When execution crosses a process boundary — an HTTP call, a gRPC
request, a Kafka message — the in-memory Context cannot travel by
reference. It must be serialized into the transport's metadata on the
sending side and deserialized back into a Context on the receiving
side.

### TextMapPropagator

The core interface for inter-process propagation. It operates on
"carriers" — objects that support string key-value pair access, like
HTTP headers or Kafka record headers.

```text
+-----------+      headers      +-----------+
| Service A | ----------------> | Service B |
|           |                   |           |
| Context   |     traceparent   | Context   |
| with Span |     tracestate    | with Span |
+-----------+                   +-----------+
```

**`inject(Context, carrier, setter)`** — reads the Trace ID, Span
ID, and trace flags from the Context and writes them into the carrier
using the provided setter function. Called on the client side before
dispatching a request.

**`extract(Context, carrier, getter)`** — reads propagation headers
from the carrier using the provided getter function and returns a new
Context populated with the extracted trace information. Called on the
server side when a request arrives.

The setter/getter abstraction decouples the propagator from any
specific HTTP library. The same W3CTraceContextPropagator works with
HttpURLConnection, Apache HttpClient, OkHttp, Netty, and any other
carrier — only the setter/getter implementation changes.

### Injection and extraction flow

**Client side (outgoing request):**

1. Instrumentation intercepts the outgoing call (e.g., HTTP client)
2. Reads `Context.current()` to get the active Span
3. Calls `propagator.inject(context, headers, headerSetter)`
4. The propagator writes `traceparent` and `tracestate` into headers
5. The request is dispatched with the enriched headers

**Server side (incoming request):**

1. Instrumentation intercepts the incoming request
2. Calls `propagator.extract(Context.root(), headers, headerGetter)`
3. The propagator reads `traceparent` and `tracestate` from headers
4. Returns a new Context containing the extracted SpanContext
5. The server creates a new Span as a child of the extracted
   SpanContext and makes it current

The extracted SpanContext is a *remote* SpanContext — it carries the
Trace ID and parent Span ID but has no local Span object. The
server's new Span references it as its parent, linking the two
services in the same trace.

## W3C trace context

The standard propagation format, supported by default. Two headers:

### traceparent

Carries the core trace routing fields in a single dash-separated
string:

```text
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             |        |                          |                |
             version  trace-id (16 B)            parent-id (8 B)  flags
```

| Field     | Size     | Description                             |
|-----------|----------|-----------------------------------------|
| version   | 1 byte   | Format version, currently `00`          |
| trace-id  | 16 bytes | Identifies the entire distributed trace |
| parent-id | 8 bytes  | Span ID of the immediate caller         |
| flags     | 1 byte   | Bit field; `01` = sampled, `00` = not   |

The trace-id is generated once at the trace root and propagated
unchanged through every service. The parent-id changes at each hop —
each service replaces it with its own Span ID so the next service
knows which Span to parent under.

### tracestate

Optional header carrying vendor-specific key-value pairs. Multiple
tracing systems can participate in the same trace by appending their
own entries without overwriting others:

```text
tracestate: vendor1=value1,vendor2=value2
```

Each vendor reads and updates only its own entry. The header
preserves ordering — the most recently modified entry appears first,
which helps receivers identify which vendor last touched the trace.

## Baggage

A propagation mechanism distinct from trace context. Baggage carries
arbitrary user-defined key-value pairs across the entire distributed
transaction via the W3C `baggage` HTTP header.

Unlike span attributes, which are local to the span they are set on,
Baggage entries are visible to every downstream service. The data
flows one direction — from caller to callee — through the entire
call chain.

```java
// Set baggage on the sending side
Baggage baggage = Baggage.builder()
    .put("tenant.id", "acme-corp")
    .put("user.role", "admin")
    .build();

try (Scope scope = baggage.makeCurrent()) {
    // Baggage is now in the current Context
    // Outgoing calls will propagate it automatically
    callDownstreamService();
}

// Read baggage on the receiving side
String tenantId = Baggage.current().getEntryValue("tenant.id");
```

Typical uses: tenant ID for multi-tenant routing, feature flags,
user classification for downstream filtering, or correlation IDs from
external systems.

Baggage is sent to every downstream service as plain HTTP headers.
Do not put sensitive data (tokens, PII) in Baggage, and keep the
total size small — large Baggage adds overhead to every network call
in the transaction.

## Related

- [Context and propagation](context-propagation.md) - Overview
- [Signals](signals.md) - The three types of telemetry data
- [Span anatomy](span-anatomy.md) - Span fields and structure
- [API vs SDK](api-vs-sdk.md) - Interface/implementation separation

---

Return to [OpenTelemetry](_index.md)
