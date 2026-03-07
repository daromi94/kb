# Lifecycle

A Pod follows a defined lifecycle from `Pending` through `Running` to either
`Succeeded` or `Failed`.

## Pod phases

The `status.phase` field provides a high-level summary:

| Phase     | Description                                                        |
|-----------|--------------------------------------------------------------------|
| Pending   | Accepted but containers not ready; includes scheduling and pulling |
| Running   | Bound to node, at least one container running or starting          |
| Succeeded | All containers exited successfully (code 0); typical for Jobs      |
| Failed    | All containers terminated, at least one failed (non-zero exit)     |
| Unknown   | State could not be obtained; usually node communication error      |

## Container states

View with `kubectl describe pod [NAME]`:

| State      | Description                                            |
|------------|--------------------------------------------------------|
| Waiting    | Not running; pulling image or waiting for secret mount |
| Running    | Executing without issues                               |
| Terminated | Finished execution; completed successfully or failed   |

## Container probes

Kubernetes uses three probe types to manage container health:

| Probe     | Purpose                                          | On failure                        |
|-----------|--------------------------------------------------|-----------------------------------|
| Startup   | For slow-starting apps; disables other probes    | Container killed, follows restart |
| Liveness  | Is the app running? (deadlock detection)         | Container killed, follows restart |
| Readiness | Is the app ready for traffic? (loading complete) | Removed from Service endpoints    |

## Termination process

When a Pod is deleted (rolling update, node drain, resource pressure):

```
+-------------------------------+
|  1. Pod marked Terminating    |
|     Grace period timer starts |
+-------+--------------+--------+
        |              |
        v              v  (parallel)
+---------------+  +-------------------+
|  2. PreStop   |  |  Endpoint removal |
|     hook runs |  |  begins (async)   |
+-------+-------+  +-------------------+
        |
        v
+---------------+
|  3. SIGTERM   |
|     sent      |
+-------+-------+
        |
        | (after grace period)
        v
+---------------+
|  4. SIGKILL   |
|     if alive  |
+-------+-------+
        |
        v
+---------------+
|  5. Pod       |
|     removed   |
+---------------+
```

## Restart policy

The `restartPolicy` determines how the kubelet reacts when a container exits:

| Policy    | Behavior                                  | Typical use             |
|-----------|-------------------------------------------|-------------------------|
| Always    | Restart regardless of exit code (default) | Deployments, DaemonSets |
| OnFailure | Restart only on non-zero exit             | Jobs                    |
| Never     | Never restart                             | One-shot tasks          |

## Related

- [Graceful termination](graceful-termination.md) - Handling shutdown in practice

---

Return to [Pods](_index.md)
