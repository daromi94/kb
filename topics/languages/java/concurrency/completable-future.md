# CompletableFuture

CompletableFuture implements both Future and CompletionStage, providing
non-blocking composition of asynchronous tasks. Where Future is passive
(you block to get the result), CompletableFuture is active — you define
what happens when the result is ready.

## Orchestration patterns

### Sequential chaining

**`thenApply(Function)`:** Transforms the result synchronously. Analogous
to `Stream.map()`.

**`thenCompose(Function)`:** Transforms the result into another
CompletableFuture and flattens. Analogous to `Stream.flatMap()` — prevents
nesting CompletableFuture inside CompletableFuture.

### Parallel combination

**`thenCombine(other, BiFunction)`:** Waits for two futures and combines
their results.

**`allOf(f1, f2, ...)`:** Completes when all provided futures complete.
Returns CompletableFuture\<Void\> — query individual futures for results.
This is the basis of the **scatter-gather** pattern: fan out independent
requests in parallel, then combine results after all complete.

### Competitive execution

**`acceptEither(other, Consumer)`:** Acts on whichever of two futures
completes first (normal completion only).

**`anyOf(f1, f2, ...)`:** Completes as soon as any provided future
completes.

## Thread management

Each method comes in three variants:

| Variant                        | Runs on                     |
|--------------------------------|-----------------------------|
| `thenApply(fn)`                | Unspecified                 |
| `thenApplyAsync(fn)`           | `ForkJoinPool.commonPool()` |
| `thenApplyAsync(fn, executor)` | The provided executor       |

The non-async variant makes no guarantee about which thread runs the
action. In practice, it is often the completing thread or the calling
thread, but the specification deliberately leaves this unspecified.

Use the executor variant to isolate I/O-bound work from the common pool.

## Exception handling

Exceptions pipeline through the stage chain rather than surfacing only at
`get()`:

**`exceptionally(Function)`:** Recovers from failure by providing a
fallback value. Analogous to a catch block.

**`handle(BiFunction)`:** Receives both the result (or null) and the
exception (or null). Transforms the output regardless of success or
failure — more flexible than `exceptionally()`.

## Manual completion

Unlike Future, a CompletableFuture can be completed explicitly:

```java
CompletableFuture<String> cf = new CompletableFuture<>();

cf.complete("done");

cf.completeExceptionally(new RuntimeException("failed"));
```

This makes CompletableFuture useful as a callback bridge — wrap a
callback-based API and expose it as a future.

## Timeouts

CompletableFuture stages can wait indefinitely if a downstream service
hangs. Two methods enforce liveness boundaries:

**`orTimeout(long timeout, TimeUnit unit)`:** Completes the future
exceptionally with a TimeoutException if it has not completed within
the given duration.

**`completeOnTimeout(T value, long timeout, TimeUnit unit)`:** Completes
the future with the provided fallback value instead of failing. Useful
when a degraded response is acceptable.

```java
CompletableFuture.supplyAsync(() -> fetchFromRemote(), ioExecutor)
    .completeOnTimeout("cached-fallback", 5, TimeUnit.SECONDS)
    .thenApply(this::process);
```

## Avoiding sequential traps

When processing a collection of futures, do not call `join()` inside a
lazy stream pipeline that also creates the futures. Intermediate stream
operations are lazy — this causes each future to be created and joined
before the next one starts, turning parallel work into sequential work.

Separate creation from result retrieval:

```java
// Create all futures first (they start executing immediately)
List<CompletableFuture<String>> futures = ids.stream()
    .map(id -> CompletableFuture.supplyAsync(() -> fetch(id), executor))
    .toList();

// Then collect results
List<String> results = futures.stream()
    .map(CompletableFuture::join)
    .toList();
```

---

Return to [Concurrency](_index.md)
