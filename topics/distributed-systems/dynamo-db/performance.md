# Performance

DynamoDB targets low single-digit millisecond latency for every request,
not just median response times. Predictable performance matters more than
raw speed — high tail latency in one service amplifies through upstream
callers and degrades the entire user experience.

## Request routing

The partition key is hashed to determine which storage node holds an
item. A request router uses this hash to contact the correct node
directly, avoiding any scanning. Routing metadata lives in MemDS, a
distributed in-memory datastore that holds partition-to-node mappings
in a highly compressed form. MemDS eliminates the bimodal latency
problem of traditional caches: even on a local cache hit, the request
router sends an asynchronous refresh to MemDS so the backing
infrastructure always sees constant traffic and stays warm.

## Storage

Each partition stores data in a B-tree on SSD alongside a write-ahead
log (WAL). Reads hit the B-tree; writes append to the WAL first for
durability before updating the tree.

## Admission control

Maintaining single-digit latency under traffic spikes requires dynamic
resource management at multiple levels.

| Mechanism         | Scope     | Behavior                                           |
|-------------------|-----------|----------------------------------------------------|
| On-demand scaling | Table     | Instantly handles up to 2x previous peak           |
| Bursting          | Partition | Taps unused capacity for short-lived spikes        |
| GAC               | Table     | Tracks global token use to prevent noisy neighbors |
| Split for consume | Partition | Splits hot partitions by observed key distribution |

Global Admission Control (GAC) uses a token-bucket model. Each storage
node reports its consumption to a central tracker, which balances
capacity across partitions so that one hot partition cannot starve
others sharing the same table allocation.

---

Return to [DynamoDB](_index.md)
