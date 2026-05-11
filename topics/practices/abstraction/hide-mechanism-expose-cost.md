# Hide mechanism, expose cost

An abstraction should hide the mechanism, but never the cost. Users
should be able to reason about performance without going deep into the
implementation.

## The SQL cautionary tale

SQL declares *what* data the query needs and hides *how* the engine
fetches it. The same query can run as an index lookup or a full table
scan, a hash join or a nested loop, in memory or spilled to disk — and
nothing in the query reveals which.

The cost can vary by orders of magnitude, invisibly from inside the
abstraction. SQL hides the mechanism well, and the cost with it.

## What "cost" means

For a distributed system, cost has three dimensions:

- **Latency.** Worst-case and tail behavior under load
- **Throughput.** Sustainable rate and how it scales
- **Blast radius.** What fails together when something fails

A good abstraction lets the user predict each one. If predicting any of
them requires going deep into the implementation, the abstraction is
hiding the wrong things.

---

Return to [Abstraction](_index.md)
