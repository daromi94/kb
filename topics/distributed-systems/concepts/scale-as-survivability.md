# Scale as survivability

A distributed system's scaling limit is not its throughput, latency,
or total capacity, but its ability to keep recovering as components
fail. Maximum scale is set by the recovery architecture, not by
available disk: once a node holds more state than the cluster can
rebuild between failures, growing it further only makes the system
less reliable.

## Recovery is the binding constraint

A node's recovery time grows with the state it holds. Rebuilding a
failed node streams its data from surviving replicas over the network,
so recovery time rises in proportion to per-node state.

Once recovery time exceeds the cluster's mean time between failures,
nodes fail faster than they can be rebuilt, cascading into quorum
loss. Past that threshold, a node cannot be made reliable by adding
replicas — it is too large to recover before the next failure arrives.

## Bounded parts, unbounded whole

Unbounded scale at the system level requires strictly bounded state at
the node level. Cap the state any single node must rebuild, and
recovery time stays short and predictable, however large the cluster
grows.

Two techniques keep per-node state bounded. Sharding adds nodes instead
of enlarging them, keeping each node's share roughly constant as total
data grows. Tiering cold data to object storage shrinks the state a
replacement node must restore. Both decouple total data size from
recovery time, so the cluster keeps rebuilding and surviving as it
scales.

This favors scaling out over scaling up. Enlarging nodes lengthens
recovery and erodes survivability; adding bounded nodes holds recovery
time constant, and survivability with it.

---

Return to [Concepts](_index.md)
