# Replicated state machine

To survive node failures without losing committed state, a system
can run several copies of its state machine in lockstep. A
Replicated State Machine (RSM) achieves this by agreeing on an
ordered command log and replaying it deterministically on every
replica.

The underlying principle is deterministic replay: replicas that
start in the same state and apply the same ordered commands through
a deterministic state machine reach the same final state. The
cluster only has to agree on the log; the state follows
automatically.

## Components

1. **Deterministic state machine.** The application logic — a ledger
   engine, a key-value store, a configuration store. Given the same
   input, it always produces the same output.
2. **Replicated log.** An ordered, append-only sequence of commands.
   The cluster replicates the log of *actions*, not the resulting
   state.
3. **Consensus protocol.** The algorithm — Paxos, Raft, Viewstamped
   Replication — that ensures every replica agrees on the exact log
   order despite network partitions, packet loss, and node failures.

```text
           +--------+
           | Client |
           +---+----+
               |
               v
     +---------+---------+
     |      Leader       |
     | +---------------+ |
     | | State machine | |
     | +---------------+ |
     | | Log: A B C    | |
     +---------+---------+
               |
               | replicate (consensus)
               |
       +-------+-------+
       v               v
+------+-----+    +----+-------+
| Follower   |    | Follower   |
| State m.   |    | State m.   |
| Log: A B C |    | Log: A B C |
+------------+    +------------+
```

## Replicate the log, not the state

Replicating raw memory state across machines is expensive and
brittle. An RSM replicates the smaller command log instead and lets
each replica re-derive its state by replaying it. The log is the
source of truth; state is its product.

## Determinism is mandatory

If the state machine reads wall clocks, RNGs, or any other
non-deterministic input, replicas diverge. Such values must be lifted
into the log: the leader generates them and writes them as log
entries every replica reads back deterministically.

## Quorum writes

An RSM does not need every replica online. A write succeeds once a
strict majority — a quorum — has durably appended it.

The leader appends the command locally, sends it to followers, waits
for a quorum of ACKs, then applies the command and replies to the
client. Any future quorum overlaps with this one, so the command
survives any single node loss, including the leader's.

---

Return to [Concepts](_index.md)
