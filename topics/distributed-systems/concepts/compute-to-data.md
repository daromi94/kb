# Compute-to-data

Compute-to-data sends the program to the data instead of pulling the data
to the program. When a dataset is far larger than the program that
processes it, that program runs on the node holding the data and returns
only the reduced result.

## The economics

The traditional model is data-to-compute: a program pulls the data into
itself, computes a result, and writes it back. That holds while the data
is small.

Once a dataset reaches terabytes and the program is only a few kilobytes,
moving the data dominates the cost. Network transfer is far slower than a
local read. Moving computation is cheap; moving data is expensive.

## Where it appears

The pattern appears at every layer of a data system. A batch scheduler
places each task on a node that already stores its input block. A
distributed database routes a query to the replicas that own the relevant
partition, computes there, and returns only the aggregated result. An
object store can run code next to the objects instead of shipping them to
a client. A query engine pushes filters and projections down into the
storage layer — predicate pushdown.

**Predicate pushdown:** evaluating filters and projections at the storage
layer so that only the needed rows and columns cross the network, instead
of shipping whole tables to the query engine.

## When to move data instead

Compute-to-data is not always the right move; weigh the sizes against the
costs. Ship the program when the data is large and the program is small
and reusable. Move the data when it is small, or when the work needs
specialized hardware, such as GPUs, that exists only in certain places. In
both cases, push the computation as close to the source as possible, so
that whatever crosses each boundary is already reduced.

---

Return to [Concepts](_index.md)
