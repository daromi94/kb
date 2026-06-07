# MTBF and MTTR

A system's availability is set by how often it fails and how long
each recovery takes. Two metrics capture these, and together they
give the steady-state availability:

$$\text{Availability} = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$$

| Metric | Name                       | Measures                        |
|--------|----------------------------|---------------------------------|
| MTBF   | Mean time between failures | Average uptime between failures |
| MTTR   | Mean time to recovery      | Average time to restore service |

MTBF is fixed by the hardware and environment, so software raises
availability by driving MTTR down.

## Mean time between failures

MTBF is the average operational time between failures of a repairable
component. It reflects the reliability of the hardware, network, and
physical environment — conditions the software architecture does not
control.

Independent failures compound at scale. A single commodity server
with a 3-year MTBF fails rarely, but a cluster of 1,000 such servers
sees a hardware failure roughly every 26 hours. The more nodes a
system spans, the more often some component in it is down.

## Mean time to recovery

MTTR is the average time to restore a failed component to full
service — not just the time to detect the fault or reboot the
machine. It covers the entire repair path: detecting the failure,
replacing or reallocating capacity, transferring state over the
network, and rebuilding the internal structures, such as indexes and
LSM trees, needed to serve traffic.

In a stateful system, MTTR is bound by data volume and network
bandwidth. A failed node holding 100 TB of state cannot recover
faster than the time to stream that 100 TB from surviving replicas.
This makes MTTR the controllable metric: bounding per-node state
through sharding cuts the transfer time and lowers MTTR directly.

## Cascading failure

In a cluster that depends on quorum, survival depends on whether
recovery finishes before the next failure arrives. If it does not,
losses accumulate faster than the system repairs them.

| Regime    | Condition        | Outcome                                             |
|-----------|------------------|-----------------------------------------------------|
| Stable    | MTTR $\ll$ MTBF  | A node recovers before the next fails; quorum holds |
| Cascading | MTTR $\geq$ MTBF | A second node fails mid-recovery; quorum is lost    |

When rebuilding a node takes longer than the mean time between
failures, a second node fails before the first recovers. The cluster
loses nodes faster than it restores them, quorum breaks, and the
system stops serving. Bounding per-node state keeps MTTR well below
MTBF and holds the cluster in the stable regime.

---

Return to [Concepts](_index.md)
