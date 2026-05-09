# CoDel

Controlled Delay (CoDel) is an active queue management algorithm
that sheds load based on how long work has been waiting, not how
much work is queued. It targets bufferbloat: the latency collapse
that happens when a queue stays full instead of draining.

## Why tail-drop fails under sustained load

A tail-drop queue accepts requests until its capacity is reached,
then drops on new arrivals. Transient bursts get absorbed and the
queue drains. Under sustained overload — arrival rate persistently
above service rate — the queue stays full and becomes a latency
amplifier.

Every accepted request waits behind the full backlog. By the time
a worker pulls a request off the queue, the client has already
timed out. The system burns cycles producing results no one is
waiting for, which compounds the overload.

The defect is structural: a length-based limit treats a 10,000-item
queue that drains in 1 ms the same as one that drains in 30 s.

## Sojourn time as the signal

CoDel measures **sojourn time**: how long each item waits in the
queue, computed at dequeue as `dequeue_time - enqueue_time`.
Brief spikes drain quickly and keep sojourn time low — a healthy
queue. When the queue stays backed up, even shallowly, sojourn
time rises and stays high. That persistence is the overload
signal.

Two parameters drive the algorithm:

| Parameter | Default | Meaning                                      |
|-----------|---------|----------------------------------------------|
| TARGET    | 5 ms    | Acceptable maximum sojourn time              |
| INTERVAL  | 100 ms  | Window for distinguishing burst from chronic |

## Detecting chronic overload

CoDel ignores transient queueing. It enters a dropping state only
when sojourn time stays above TARGET for a full INTERVAL — the
queue never fully drained during the window.

Conceptually:

```text
min(sojourn_time over INTERVAL) > TARGET -> chronic overload
```

## Why time-based shedding works

CoDel changes how a database, query engine, or coordination layer
behaves under load:

- **Spends compute on live requests.** Requests past their client
  timeout are dropped before execution. Cycles go to work whose
  result will still be read.
- **Caps wait time.** Requests that sit longer than TARGET get
  dropped, so the ones that survive don't wait much longer than
  that.
- **Self-tunes across hardware.** A 5 ms target means the same
  thing on any machine. A 10,000-item queue does not — its
  meaning shifts with every CPU upgrade or workload change.

## Related

- [Metastable failures](metastable-failures.md) - Self-sustaining failure states
- [Blast radius reduction](blast-radius-reduction.md) - Containment through compartmentalization

---

Return to [Concepts](_index.md)
