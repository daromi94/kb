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

// Some external event completes it later
cf.complete("done");

cf.completeExceptionally(new RuntimeException("failed"));
```

This makes CompletableFuture useful as a callback bridge — wrap a
callback-based API and expose it as a future.

## Related

- [Future](future.md) - The blocking predecessor
- [Fork join pool](fork-join-pool.md) - Default pool for async methods
- [Executor service](executor-service.md) - Custom pools for async variants

---

Return to [Concurrency](_index.md)
