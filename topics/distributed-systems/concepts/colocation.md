# Colocation

Colocation places things that work together near each other in the
network, so that few or no hops separate them. Those things might be a
pair of processes, related datasets, or a service and the data it reads.
The same node is ideal; a shared rack, zone, or region is next best.

It is the design-time counterpart of data locality. Locality is resolved
at runtime, for example when a scheduler sends each task to the node
that already holds its data. Colocation is decided earlier, when you
design a schema or plan a deployment.

---

Return to [Concepts](_index.md)
