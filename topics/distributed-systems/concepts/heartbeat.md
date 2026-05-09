# Heartbeat

A periodic signal that lets nodes prove they are alive. In a distributed
system you cannot distinguish a slow process, a congested network, or a
crashed node, so heartbeats provide the mechanism for the cluster to
decide when a node should be considered dead.

## Mechanism

A sender (typically the leader) transmits a small message at a fixed
interval. Each receiver resets a local timer on every arrival. If the
timer expires before the next heartbeat, the receiver assumes the sender
has failed and triggers recovery such as a new leader election.

| Component    | Role                                                                        |
|--------------|-----------------------------------------------------------------------------|
| **Interval** | How often the heartbeat is sent                                             |
| **Timeout**  | How long to wait before declaring failure                                   |
| **Payload**  | Usually tiny; may include the generation clock (term) as proof of authority |
| **Reaction** | Trigger a leader election or mark a partition for rebalancing               |

## Timing inequality

To prevent false positives the timeout must satisfy:

$$\text{Timeout} > \text{Request Interval} + \text{RTT}$$

- **Request interval** must exceed RTT to avoid saturating the network
  buffer with piled-up packets.
- **Timeout** must exceed one full request/response cycle plus a safety
  margin; otherwise any jitter causes a spurious failure declaration.

In production the formula is usually expanded with a multiplier (3x-5x)
to tolerate multiple lost packets:

$$\text{Timeout} > (\text{Request Interval} \times \text{Max Retries}) + \text{Jitter Buffer}$$

Violating the inequality causes flapping: healthy nodes are marked dead,
elections churn continuously, and split-brain risk increases because
multiple nodes attempt to become leader.

## Challenges

**Network jitter.** An aggressive timeout (e.g. 200 ms) turns transient
spikes into false failures, and the cluster spends its resources
electing leaders instead of processing data.

**Stop-the-world pauses.** A long GC pause in languages like Java can
freeze all threads. The node is physically healthy, but if the pause
exceeds the heartbeat timeout the rest of the cluster declares it dead.

## Improvements

**Randomized election timeouts.** Giving nodes different timeout windows
prevents thundering herds where every follower starts an election
simultaneously after a missed heartbeat.

**Phi accrual failure detector.** Instead of a binary up/down decision,
systems like Cassandra track heartbeat arrival history and compute a
continuous suspicion level ($\phi$). Action is taken only when suspicion
crosses a high threshold, reducing false positives under variable
network conditions.

**Two-way heartbeats.** A mesh where every node pings its neighbors
detects partial network partitions that a leader-to-follower scheme
would miss (e.g. A can reach B, but B cannot reach C).

## Heartbeats and leases

A leader is granted authority for a bounded time window (the lease) and
must successfully heartbeat a majority of followers to renew it. If
heartbeats stop, the lease expires and the leader's authority is
automatically revoked, preventing zombie leaders from corrupting data.

---

Return to [Concepts](_index.md)
