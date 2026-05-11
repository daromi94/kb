# Hide mechanism, expose cost

An abstraction should hide the mechanism, but never the cost. Users
should be able to reason about cost without going deep into the
implementation.

## The SQL cautionary tale

SQL declares *what* data the query needs and hides *how* the engine
fetches it. The same query can run as an index lookup or a full table
scan, a hash join or a nested loop, in memory or spilled to disk — and
nothing in the query reveals which.

The cost can vary by orders of magnitude, invisibly from inside the
abstraction. SQL hides the mechanism well, and the cost with it.

## What "cost" means

Cost has many dimensions: latency, throughput, blast radius, and more.
A good abstraction lets the user predict each one without going deep
into the implementation. Otherwise, it's hiding the wrong things.

---

Return to [Abstraction](_index.md)
