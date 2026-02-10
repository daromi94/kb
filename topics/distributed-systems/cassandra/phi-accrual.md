# Phi accrual failure detector

Cassandra uses the Phi Accrual Failure Detector instead of binary
heartbeats to decide whether a node is alive or dead. By treating failure
as a statistical probability rather than a binary event, the detector
remains stable through network jitter and GC pauses that would cause
simpler systems to flap.

## The problem with binary heartbeats

A fixed-timeout heartbeat marks a node dead when a single message is late.
Setting the timeout too low causes false positives — healthy nodes marked
dead, triggering unnecessary data rebalancing. Setting it too high delays
detection of genuinely failed nodes.

## Suspicion level

The detector maintains a sliding window of arrival times for recent gossip
messages from each peer. It builds a distribution of intervals to learn
what "normal" looks like for that specific connection.

When a message is late, the detector calculates a suspicion value (phi):

- **Low phi:** Heartbeat is only slightly late; likely minor jitter
- **Rising phi:** As silence continues, suspicion grows
- **High phi:** The probability the node is alive becomes statistically
  insignificant

Because the detector learns each connection's baseline, it adapts
automatically. A naturally slower cross-DC link will not trigger false
convictions.

## Conviction process

When phi crosses the configured `phi_convict_threshold`, the gossiper
convicts the node:

1. The node's status is set to `DOWN` in the local gossip state
2. Internal components (`StorageService`) are notified
3. The coordinator stops routing queries to that node
4. Writes intended for the downed node are stored as hints for later
   replay

## Tuning

The `phi_convict_threshold` controls sensitivity:

- Lower values (e.g. 8) convict faster — better for stable networks
- Higher values (e.g. 12) tolerate more jitter — better for unreliable
  links

## Binary vs accrual

| Feature     | Binary heartbeat          | Phi accrual                            |
|-------------|---------------------------|----------------------------------------|
| Logic       | Up or down after timeout  | Probability scale from 0 to infinity   |
| Sensitivity | Fixed timeout             | Adaptive to observed arrival history   |
| Reaction    | Sudden; prone to flapping | Gradual suspicion accumulation         |
| Philosophy  | No heartbeat means dead   | How likely should I have heard by now? |

## Related

- [Gossip](gossip.md) - Provides the heartbeat data the detector analyzes
- [Fault tolerance](fault-tolerance.md) - How conviction feeds into recovery mechanisms
- [Query routing](query-routing.md) - How the coordinator uses gossip status

---

Return to [Cassandra](_index.md)
