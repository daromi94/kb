# Uniform access principle

The uniform access principle (UAP) states that all services offered by a
module should be available through a single notation that does not reveal
whether the service is implemented via storage or computation. A client
should neither know nor care how a value is produced.

Coined by Bertrand Meyer in *Object-Oriented Software Construction*.

## Storage vs computation

A `Circle` might store its area as a field updated when the radius changes,
or compute it on the fly. Under UAP, both cases use the same syntax:

```python
circle.area # stored field or computed — caller cannot tell
```

If the implementation switches from cached to calculated (or vice versa),
client code is unaffected because the access notation never changed. This
hides the "storage vs computation" design decision, which is the specific
form of encapsulation UAP targets.

## The performance objection

Critics argue that syntax should distinguish cheap field access from
potentially expensive computation. Three responses:

**Measure first:** Assuming a computation is slow before profiling is
premature optimization.

**Memoization:** If a computation is costly, the object can cache the result
internally. The interface stays simple while performance is preserved.

**Break UAP for I/O:** When a property would trigger a database query or
network call, use an explicit name like `fetchData()` to signal the cost.
UAP applies to in-memory decisions, not I/O boundaries.

## Related

- [Abstraction](abstraction.md) - UAP is a specific form of implementation hiding

---

Return to [Abstraction](_index.md)
