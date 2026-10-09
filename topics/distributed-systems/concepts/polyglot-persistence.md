# Polyglot persistence

Polyglot persistence stores data across several specialized systems and
keeps them consistent by designating one as the system of record and
deriving the rest from it. The primary database holds the authoritative
state; caches and search indexes are derived views rebuilt from its writes,
never written to directly.

## Propagating writes

Every write goes to the system of record. A change data capture stream
emits each committed change as an event, and downstream consumers apply
that event to update the search index and invalidate the cache. Because
changes flow one way out of the system of record, the derived stores
converge on its state without coordinating with each other.

**Change data capture (CDC):** a stream of every committed change to the
primary database, published as events for other systems to consume.

```text
              write
                |
                v
       +-----------------+
       |    Database     |  system of record
       +--------+--------+
                | CDC event
                v
       +-----------------+
       |     Stream      |
       +--------+--------+
                |
        +-------+-------+
        |               |
        v               v
 +--------------+ +--------------+
 | Search index | |    Cache     |
 |   (update)   | | (invalidate) |
 +--------------+ +--------------+
```

Propagation is asynchronous, so a derived store reflects each write only
after the event reaches it. The derived stores are eventually consistent
with the system of record.

---

Return to [Concepts](_index.md)
