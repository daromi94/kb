# Graceful termination

Kubernetes terminates healthy pods routinely — rolling updates, node
drains, resource pressure. Applications must handle SIGTERM and shut down
cleanly to minimize user impact and speed recovery.

## What the application should do

On SIGTERM, the process should:

- Stop accepting new work (close listeners, deregister from queues)
- Finish in-flight requests and drain connections
- Save state if needed (flush buffers, checkpoint)
- Close long-lived connections (database pools, WebSocket streams)
- Exit with code 0

The grace period timer starts as soon as Kubernetes decides to terminate
the pod. PreStop hook execution and SIGTERM delivery both count against
this budget.

## preStop hook

A command or HTTP request executed in the container before SIGTERM is
sent. Useful when the application does not handle SIGTERM natively — for
example, third-party software or legacy services where modifying the
signal handler is impractical.

```yaml
lifecycle:
  preStop:
    exec:
      command: [ "/bin/sh", "-c", "nginx -s quit && sleep 5" ]
```

```yaml
lifecycle:
  preStop:
    httpGet:
      path: /shutdown
      port: 8080
```

SIGTERM is sent after the preStop hook completes (or times out), not in
parallel. Both share the same grace period budget.

## terminationGracePeriodSeconds

Default is 30 seconds. If the application needs longer to drain, increase
it in the Pod spec:

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: app
      image: app:latest
```

If the process exits before the grace period expires, Kubernetes proceeds
immediately — there is no unnecessary wait.

## Common pitfalls

- **Ignoring SIGTERM:** The process receives SIGKILL after the grace
  period and drops in-flight work. Always handle the signal.
- **PID 1 trap:** Shell scripts as entrypoints may not forward signals.
  Use `exec` to replace the shell, or use `tini` / `dumb-init`.
- **Grace period too short:** Long-running requests (reports, batch
  processing) need a grace period that covers the worst-case drain time.
- **Endpoint race:** Endpoint removal propagates asynchronously. A brief
  `sleep` in the preStop hook (2-5 seconds) gives kube-proxy and ingress
  controllers time to update before the app stops serving.

---

Return to [Pods](_index.md)
