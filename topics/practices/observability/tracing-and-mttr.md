# Tracing and MTTR

Distributed tracing lowers mean time to recovery (MTTR), the time it
takes to restore service after an incident. It links a single request
across every service it touches, so you can isolate the failing
component instead of searching each service's logs separately.

## The problem tracing solves

With only metrics and logs, locating a fault across many services is
slow. When a request times out, the entry gateway's log shows only that,
not which downstream dependency caused it. Each service writes to its
own logs, so finding the responsible one means opening them one at a
time and reconstructing the request path by hand.

## From alert to root cause

Tracing turns that manual search into a direct path through the three
signals:

1. A metric alert fires, flagging a degraded request, such as a latency
   spike or a rising error rate.
2. You pull the trace for that request. Its spans expose the slow or
   failing step, isolating the specific service, database query, or
   network hop responsible.
3. That span points you to the logs of that one component, where the
   high-fidelity detail explains the failure.

Each signal has one job: metrics detect, traces localize, logs explain.
Metrics and logs answer how much and what; the trace supplies the where
that connects them.

## Why this moves MTTR

MTTR covers the whole repair path: detecting the failure, diagnosing it,
and restoring service. Tracing targets the diagnosis stage, which is
where the time goes when many services are involved. Replacing that
manual log search with a single trace lookup takes that time straight
off recovery.

---

Return to [Observability](_index.md)
