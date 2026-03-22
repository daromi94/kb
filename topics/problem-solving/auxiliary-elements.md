# Auxiliary elements

Introduce a new component into a problem to make the path to a
solution visible. The element does not change the problem — it
embeds it into a richer context where known methods apply.

## How it works

When no direct connection exists between the data and the unknown,
an auxiliary element reveals hidden relationships. It transforms an
unfamiliar configuration into a familiar pattern, bridges disparate
pieces of data, or artificially creates a condition that a powerful
theorem requires.

## Examples

| Element               | Effect                                              |
|-----------------------|-----------------------------------------------------|
| Sentinel node         | Eliminates empty-list edge cases in insert/delete   |
| Intermediate hash map | Bridges input to answer with O(1) lookups           |
| Virtual graph node    | Reduces multi-source to single-source shortest path |

## Application questions

- Is there a known method that almost applies? What element must
  be added to use it?
- Can you introduce something new that connects disparate pieces
  of the given data?
- Can you add a component that eliminates special cases?

## Related

- [Analogy](analogy.md) - Solving by structural similarity
- [The four-phase method](four-phase-method.md) - Overarching process

---

Return to [Problem-solving](_index.md)
